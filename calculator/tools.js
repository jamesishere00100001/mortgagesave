// Small calculators behind the guide pages. Plain arithmetic on top of calc.js,
// so payments are rounded to the penny exactly as the app does.
import { monthlyPayment, OVERPAYMENT_CAP_PERCENT } from './calc.js';

/**
 * Overpayment allowance for the current year.
 * a: { balance, allowancePercent, overpaidSoFar, monthsLeft, ercPercent }
 */
export function allowance(a) {
  const pct = a.allowancePercent ?? OVERPAYMENT_CAP_PERCENT;
  const yearly = (a.balance * pct) / 100;
  const used = Math.max(a.overpaidSoFar || 0, 0);
  const remaining = Math.max(yearly - used, 0);
  const monthsLeft = Math.min(Math.max(Math.round(a.monthsLeft || 12), 1), 12);
  const over = Math.max(used - yearly, 0);
  return {
    yearly,
    monthlyEven: yearly / 12,
    remaining,
    perMonthLeft: remaining / monthsLeft,
    overBy: over,
    ercOnOver: (over * (a.ercPercent || 0)) / 100,
  };
}

/**
 * What happens when a fixed deal ends.
 * e: { balance, yearsLeft, currentRate, svr, newRate }
 */
export function dealEnd(e) {
  const n = Math.round(e.yearsLeft * 12);
  const pay = (rate) => monthlyPayment(e.balance, rate / 100 / 12, n);
  const current = pay(e.currentRate);
  const svr = pay(e.svr);
  const newDeal = e.newRate > 0 || e.newRate === 0 ? pay(e.newRate) : null;
  return {
    months: n,
    current,
    svr,
    newDeal,
    svrJump: svr - current,
    newDealChange: newDeal == null ? null : newDeal - current,
    svrVsNewPerYear: newDeal == null ? null : (svr - newDeal) * 12,
  };
}

/** Value after `months` of paying `monthly` into something growing at `annualRate` (monthly compounding). */
export function futureValue(monthly, annualRate, months) {
  const r = annualRate / 100 / 12;
  if (r === 0) return monthly * months;
  return monthly * ((Math.pow(1 + r, months) - 1) / r);
}

/**
 * Overpay the mortgage or put the same money in savings.
 * s: { monthly, years, mortgageRate, savingsRate, taxRate }
 * Overpaying is worth the interest you no longer pay, so it grows at the mortgage rate.
 */
export function overpayOrSave(s) {
  const months = Math.round(s.years * 12);
  const paidIn = s.monthly * months;
  const afterTax = s.savingsRate * (1 - (s.taxRate || 0) / 100);
  const overpay = futureValue(s.monthly, s.mortgageRate, months);
  const save = futureValue(s.monthly, afterTax, months);
  return {
    months,
    paidIn,
    afterTaxSavingsRate: afterTax,
    overpayGain: overpay - paidIn,
    saveGain: save - paidIn,
    difference: overpay - save,
    winner: Math.abs(overpay - save) < 0.5 ? 'tie' : overpay > save ? 'overpay' : 'save',
  };
}
