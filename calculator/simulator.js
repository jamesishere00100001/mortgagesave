// Mortgage Save repayment simulator (web).
// A port of MortgageApp/Services/RepaymentSimulator.swift (monthly interest only,
// which is the UK behaviour) so the lump-sum page gives the same figures as the
// app's lump-sum tool. If you change the maths in one, change it in the other
// and re-run simulator.test.mjs.

export const MODE = { reduceTenure: 'reduceTenure', reduceEMI: 'reduceEMI' };

function level(balance, rate, months) {
  if (months <= 0) return balance;
  const r = rate / 100 / 12;
  if (r === 0) return balance / months;
  const f = Math.pow(1 + r, months);
  return (balance * r * f) / (f - 1);
}

/**
 * d: { loan, termYears, dealRate, dealYears, svr }
 * o: { mode, monthlyExtra, lumpSum, lumpSumMonth (1-based), ercPercent }
 * Returns { months, monthlyPayment, totalInterest, totalCharges, totalPaid } or null.
 */
export function simulate(d, o = {}) {
  if (!(d.loan > 0) || !(d.termYears > 0)) return null;
  const mode = o.mode || MODE.reduceTenure;
  const monthlyExtra = o.monthlyExtra || 0;
  const lumpSum = o.lumpSum || 0;
  const lumpSumMonth = o.lumpSumMonth || 1;
  const ercPercent = o.ercPercent || 0;

  const totalMonths = Math.round(d.termYears * 12);
  const dealMonths = Math.round(d.dealYears * 12);
  let balance = d.loan;
  let interestTotal = 0;
  let chargesTotal = 0;
  let paidTotal = 0;
  let month = 0;
  let payment = 0;
  let lastPaymentRateChange = -1;
  // Balance with no prepayments: in reduce-tenure mode the payment at a rate change
  // is set from this, so prepayments keep shortening the term.
  let scheduledBalance = d.loan;
  let scheduledPayment = 0;

  const annualRate = (m) => (m < dealMonths ? d.dealRate : d.svr);
  const cap = totalMonths + 12 * 50;

  while (balance > 0.005 && month < cap) {
    const rate = annualRate(month);
    const phase = month < dealMonths ? 0 : 1;

    if (lastPaymentRateChange !== phase) {
      const monthsLeft = Math.max(totalMonths - month, 1);
      scheduledPayment = level(scheduledBalance, rate, monthsLeft);
      if (lastPaymentRateChange === -1 || mode === MODE.reduceEMI || scheduledBalance <= 0.005) {
        payment = level(balance, rate, monthsLeft);
      } else {
        payment = scheduledPayment;
      }
      lastPaymentRateChange = phase;
    }

    const interest = (balance * rate) / 100 / 12;
    if (scheduledBalance > 0.005) {
      const scheduledInterest = (scheduledBalance * rate) / 100 / 12;
      scheduledBalance -= Math.min(scheduledPayment - scheduledInterest, scheduledBalance);
    }

    let extra = monthlyExtra;
    if (month + 1 === lumpSumMonth) extra += lumpSum;

    let principal = Math.min(payment - interest, balance);
    if (principal < 0) return null; // payment cannot cover interest
    let prepaid = Math.min(extra, balance - principal);
    if (prepaid < 0) prepaid = 0;

    let charge = 0;
    if (month < dealMonths && ercPercent > 0) charge = (prepaid * ercPercent) / 100;

    principal += prepaid;
    balance -= principal;
    interestTotal += interest;
    chargesTotal += charge;
    paidTotal += interest + principal + charge;
    month += 1;

    if (mode === MODE.reduceEMI && prepaid > 0 && balance > 0.005) {
      payment = level(balance, annualRate(month), Math.max(totalMonths - month, 1));
    }
  }

  return {
    months: month,
    monthlyPayment: Math.round(payment * 100) / 100,
    totalInterest: interestTotal,
    totalCharges: chargesTotal,
    totalPaid: paidTotal,
  };
}

/** RepaymentSimulator.compare: baseline (no prepayments) against the options. */
export function compare(d, o) {
  const baseline = simulate(d, { ...o, monthlyExtra: 0, lumpSum: 0 });
  const withPrepayment = simulate(d, o);
  if (!baseline || !withPrepayment) return null;
  return {
    baseline,
    withPrepayment,
    interestSaved: baseline.totalInterest - withPrepayment.totalInterest,
    netSaving: baseline.totalPaid - withPrepayment.totalPaid,
    monthsSaved: baseline.months - withPrepayment.months,
  };
}
