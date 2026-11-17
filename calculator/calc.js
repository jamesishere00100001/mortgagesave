// Mortgage Save calculation engine (web).
// A line-for-line port of MortgageApp/Services/MortgageCalculator.swift so the
// web calculator and the iOS app give identical figures. If you change the
// maths in one, change it in the other and re-run calc.test.mjs.

export const OVERPAYMENT_CAP_PERCENT = 10; // UK market limit from MarketRules.swift

export const LIMITS = {
  minLoan: 1_000,
  maxLoan: 10_000_000,
  maxTermYears: 50,
  maxRate: 25,
};

/** Standard amortisation formula, rounded to the penny like the app. */
export function monthlyPayment(principal, monthlyRate, n) {
  if (!(monthlyRate > 0)) return principal / n;
  const f = Math.pow(1 + monthlyRate, n);
  const payment = principal * ((monthlyRate * f) / (f - 1));
  return Math.round(payment * 100) / 100;
}

/** Balance remaining after `payments` level payments. */
export function remainingBalance(principal, monthlyRate, payment, payments) {
  if (!(monthlyRate > 0)) return principal - payment * payments;
  const f = Math.pow(1 + monthlyRate, payments);
  return Math.max(principal * f - (payment * (f - 1)) / monthlyRate, 0);
}

/**
 * Validates inputs. Mirrors LoanDetails.isValid plus the UK market limits.
 * Returns an object of field -> message (empty when valid).
 */
export function validate(d) {
  const e = {};
  if (!(d.loan >= LIMITS.minLoan)) e.loan = `Enter a loan of at least £${LIMITS.minLoan.toLocaleString('en-GB')}`;
  else if (d.loan > LIMITS.maxLoan) e.loan = `Enter a loan up to £${LIMITS.maxLoan.toLocaleString('en-GB')}`;
  if (!(d.termYears > 0)) e.termYears = 'Enter the mortgage term in years';
  else if (d.termYears > LIMITS.maxTermYears) e.termYears = `Term can be up to ${LIMITS.maxTermYears} years`;
  if (!(d.dealRate >= 0) || d.dealRate > LIMITS.maxRate) e.dealRate = `Enter a rate between 0% and ${LIMITS.maxRate}%`;
  if (!(d.dealYears > 0)) e.dealYears = 'Enter how long the deal lasts';
  else if (d.termYears > 0 && d.dealYears > d.termYears) e.dealYears = 'The deal can’t be longer than the mortgage';
  if (!(d.svr >= 0) || d.svr > LIMITS.maxRate) e.svr = `Enter a rate between 0% and ${LIMITS.maxRate}%`;
  if (!(d.overpayment >= 0)) e.overpayment = 'Enter 0 or more';
  return e;
}

/** MortgageCalculator.calculateStandardPayments */
export function standardPayments(d) {
  const initialMonths = d.dealYears * 12;
  const totalMonths = d.termYears * 12;
  const initialRate = d.dealRate / 100 / 12;
  const standardRate = d.svr / 100 / 12;

  const dealPayment = monthlyPayment(d.loan, initialRate, totalMonths);
  const balanceAfterDeal = remainingBalance(d.loan, initialRate, dealPayment, Math.trunc(initialMonths));
  const remainingMonths = totalMonths - initialMonths;
  const svrPayment = remainingMonths > 0 ? monthlyPayment(balanceAfterDeal, standardRate, remainingMonths) : 0;

  const totalDeal = initialMonths * dealPayment;
  const totalSvr = remainingMonths * svrPayment;
  const totalPayable = totalDeal + totalSvr;

  return {
    months: totalMonths,
    dealMonths: initialMonths,
    svrMonths: remainingMonths,
    dealPayment,
    svrPayment,
    balanceAfterDeal,
    totalDeal,
    totalSvr,
    totalPayable,
    totalInterest: totalPayable - d.loan,
  };
}

/** Largest monthly overpayment inside the annual allowance. */
export function maxMonthlyOverpayment(loan, capPercent = OVERPAYMENT_CAP_PERCENT) {
  return (loan * (capPercent / 100)) / 12;
}

/**
 * MortgageCalculator.calculateWithOverpayment, without throwing on the cap:
 * the web page shows a warning instead and still shows the figures.
 */
export function withOverpayment(d, std) {
  const over = d.overpayment || 0;
  if (over <= 0) return null;

  let balance = d.loan;
  let months = 0;
  let totalPaid = 0;
  let dealRemaining = d.dealYears * 12;
  let rate = d.dealRate;
  const limit = d.termYears * 12 * 2; // safety limit, as in the app

  while (balance > 0 && months < limit) {
    const interest = balance * (rate / 100 / 12);
    const base = dealRemaining > 0 ? std.dealPayment : std.svrPayment;
    const payment = base + over;
    const principal = Math.min(payment - interest, balance);

    balance -= principal;
    totalPaid += Math.min(payment, principal + interest);
    months += 1;

    if (dealRemaining > 0) {
      dealRemaining -= 1;
      if (dealRemaining === 0) rate = d.svr;
    }
    if (balance < 0.01) balance = 0;
  }

  return {
    months,
    years: months / 12,
    totalPaid,
    totalInterest: totalPaid - d.loan,
    saving: std.totalPayable - totalPaid,
    monthsSaved: std.months - months,
    dealPayment: std.dealPayment + over,
    svrPayment: std.svrPayment + over,
    overCap: over > maxMonthlyOverpayment(d.loan) + 0.005,
  };
}

/** MortgageCalculator.generateAmortizationSchedule (monthly rows). */
export function schedule(d, std, includeOverpayment) {
  const over = includeOverpayment ? d.overpayment || 0 : 0;
  const rows = [];
  let balance = d.loan;
  let month = 1;
  let dealRemaining = Math.trunc(d.dealYears * 12);
  const last = Math.trunc(d.termYears * 12) + 12;

  while (balance > 0.01 && month <= last) {
    const inDeal = dealRemaining > 0;
    const rate = inDeal ? d.dealRate : d.svr;
    const base = inDeal ? std.dealPayment : std.svrPayment;
    const interest = balance * (rate / 100 / 12);
    const principal = Math.min(base + over - interest, balance);
    const closing = Math.max(balance - principal, 0);

    rows.push({
      month,
      year: Math.floor((month - 1) / 12) + 1,
      opening: balance,
      payment: base,
      overpayment: over,
      principal,
      interest,
      closing,
      rate,
      inDeal,
    });

    balance = closing;
    month += 1;
    if (dealRemaining > 0) dealRemaining -= 1;
  }
  return rows;
}

/** Rolls monthly rows up into years for the table and chart. */
export function byYear(rows) {
  const years = [];
  for (const r of rows) {
    let y = years[r.year - 1];
    if (!y) {
      y = years[r.year - 1] = { year: r.year, paid: 0, principal: 0, interest: 0, closing: 0, inDeal: r.inDeal };
    }
    y.paid += Math.min(r.payment + r.overpayment, r.principal + r.interest);
    y.principal += r.principal;
    y.interest += r.interest;
    y.closing = r.closing;
  }
  return years;
}

/** One call for the page: everything it needs, or { errors }. */
export function calculate(d) {
  const errors = validate(d);
  if (Object.keys(errors).length) return { errors };
  const std = standardPayments(d);
  const over = withOverpayment(d, std);
  const baseYears = byYear(schedule(d, std, false));
  const overYears = over ? byYear(schedule(d, std, true)) : null;
  return { errors: {}, std, over, baseYears, overYears, cap: maxMonthlyOverpayment(d.loan) };
}
