// Remortgage decision tools: 2-year vs 5-year fix, and leaving a fix early.
// A port of MortgageApp/Services/RemortgageCalculator.swift (MortgageMaths, cost,
// compareFixLengths, compareEarlyExit). Options are compared on net cost over the
// same period: interest plus fees, minus cashback. Change the maths in both.

/** Level monthly repayment, rounded to the penny. */
export function monthlyPayment(principal, annualRate, months) {
  if (!(principal > 0) || !(months > 0)) return 0;
  const r = annualRate / 100 / 12;
  const raw = r === 0 ? principal / months : (principal * r * Math.pow(1 + r, months)) / (Math.pow(1 + r, months) - 1);
  return Math.round(raw * 100) / 100;
}

/** Pays `payment` a month for up to `months`, stopping early if cleared. */
export function run(balance, annualRate, payment, months) {
  let bal = balance, paid = 0, interest = 0, count = 0;
  const r = annualRate / 100 / 12;
  while (count < months && bal > 0.005) {
    const mi = bal * r;
    const due = Math.min(payment, bal + mi);
    bal = bal + mi - due;
    paid += due;
    interest += mi;
    count += 1;
  }
  return { totalPaid: paid, interestPaid: interest, endBalance: Math.max(0, bal), monthsPaid: count };
}

/** option: { rate, years, fees = 0, addFeesToLoan = false, cashback = 0 } */
export function cost(option, balance, remainingMonths, horizonMonths, followOnRate = null, followOnFees = 0) {
  const fees = option.fees || 0;
  const cashback = option.cashback || 0;
  const loan = balance + (option.addFeesToLoan ? fees : 0);
  const payment = monthlyPayment(loan, option.rate, remainingMonths);
  const dealMonths = Math.min(option.years * 12, horizonMonths, remainingMonths);
  const first = run(loan, option.rate, payment, dealMonths);

  let totalPaid = first.totalPaid;
  let interest = first.interestPaid;
  let endBalance = first.endBalance;
  let upfront = option.addFeesToLoan ? 0 : fees;

  const laterMonths = Math.min(horizonMonths, remainingMonths) - dealMonths;
  if (laterMonths > 0 && endBalance > 0) {
    const rate = followOnRate ?? option.rate;
    const monthsLeft = remainingMonths - dealMonths;
    const laterPayment = monthlyPayment(endBalance, rate, monthsLeft);
    const second = run(endBalance, rate, laterPayment, laterMonths);
    totalPaid += second.totalPaid;
    interest += second.interestPaid;
    endBalance = second.endBalance;
    upfront += followOnFees;
  }

  return {
    monthlyPayment: payment,
    totalPaid,
    interestPaid: interest,
    upfrontFees: upfront,
    cashback,
    endBalance,
    netCost: totalPaid + upfront - cashback + endBalance - balance,
  };
}

export function compareFixLengths(balance, remainingMonths, shorter, longer, refixRate, refixFees = 0) {
  const horizon = Math.min(Math.max(shorter.years, longer.years) * 12, remainingMonths);
  const shorterCost = (rate) => cost(shorter, balance, remainingMonths, horizon, rate, refixFees);
  const longerCost = cost(longer, balance, remainingMonths, horizon);
  const shorterAtRefix = shorterCost(refixRate);

  let breakEven = null;
  let low = 0, high = 25;
  const diffLow = shorterCost(low).netCost - longerCost.netCost;
  const diffHigh = shorterCost(high).netCost - longerCost.netCost;
  if (diffLow <= 0 && diffHigh >= 0) {
    for (let i = 0; i < 60; i++) {
      const mid = (low + high) / 2;
      if (shorterCost(mid).netCost - longerCost.netCost < 0) low = mid; else high = mid;
    }
    breakEven = Math.round(((low + high) / 2) * 100) / 100;
  }
  return {
    shorter: shorterAtRefix,
    longer: longerCost,
    horizonMonths: horizon,
    shorterCostsMoreBy: shorterAtRefix.netCost - longerCost.netCost,
    breakEvenRefixRate: breakEven,
  };
}

export function compareEarlyExit(balance, remainingMonths, currentRate, monthsLeftInDeal, ercPercent, newRate, newFees) {
  const horizon = Math.min(monthsLeftInDeal, remainingMonths);
  const years = Math.max(1, Math.ceil(horizon / 12));
  const erc = (balance * ercPercent) / 100;
  const stay = cost({ rate: currentRate, years }, balance, remainingMonths, horizon);
  const leave = cost({ rate: newRate, years, fees: newFees + erc }, balance, remainingMonths, horizon);
  return { earlyRepaymentCharge: erc, stay, leave, savingFromLeaving: stay.netCost - leave.netCost };
}
