// node --test tools.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { simulate, compare, MODE } from './simulator.js';
import { allowance, dealEnd, overpayOrSave, futureValue } from './tools.js';
import { standardPayments } from './calc.js';

const near = (a, b, tol, msg) => assert.ok(Math.abs(a - b) <= tol, `${msg}: ${a} vs ${b}`);
// Same defaults as RepaymentSimulatorTests.loan()
const loan = (o = {}) => ({ loan: 1_000_000, termYears: 20, dealRate: 9, dealYears: 20, svr: 9, ...o });

// Ports of MortgageAppTests/RepaymentSimulatorTests.swift
test('baseline matches standard amortisation', () => {
  const d = loan();
  const r = simulate(d, {});
  const std = standardPayments({ ...d, overpayment: 0 });
  assert.equal(r.months, 240);
  near(r.monthlyPayment, std.dealPayment, 0.05, 'payment');
  near(r.totalPaid, std.totalPayable, 300, 'total');
});

test('zero-rate loan repays principal only', () => {
  const r = simulate(loan({ loan: 120_000, termYears: 10, dealYears: 10, dealRate: 0, svr: 0 }), {});
  near(r.totalInterest, 0, 0.01, 'interest');
  assert.equal(r.months, 120);
});

test('reduce tenure shortens term and saves interest', () => {
  const c = compare(loan(), { lumpSum: 200_000 });
  assert.ok(c.monthsSaved > 12);
  assert.ok(c.interestSaved > 0);
});

test('reduce payment keeps term and lowers payment', () => {
  const c = compare(loan(), { lumpSum: 200_000, mode: MODE.reduceEMI });
  assert.equal(c.withPrepayment.months, c.baseline.months);
  assert.ok(c.withPrepayment.monthlyPayment < c.baseline.monthlyPayment);
  assert.ok(c.interestSaved > 0);
});

test('reduce tenure saves more interest than reduce payment', () => {
  const t = compare(loan(), { lumpSum: 200_000 });
  const e = compare(loan(), { lumpSum: 200_000, mode: MODE.reduceEMI });
  assert.ok(t.interestSaved > e.interestSaved);
});

test('early repayment charge applies only during the deal', () => {
  const inDeal = simulate(loan({ dealYears: 3 }), { lumpSum: 100_000, ercPercent: 2 });
  near(inDeal.totalCharges, 2_000, 0.01, 'in deal');
  const after = simulate(loan({ dealYears: 3 }), { lumpSum: 100_000, ercPercent: 2, lumpSumMonth: 40 });
  near(after.totalCharges, 0, 0.01, 'after deal');
});

test('rate reversion raises payment', () => {
  const d = { loan: 300_000, termYears: 25, dealRate: 3, dealYears: 2, svr: 7 };
  const r = simulate(d, {});
  const std = standardPayments({ ...d, overpayment: 0 });
  assert.ok(r.monthlyPayment > std.dealPayment);
  assert.equal(r.months, 300);
});

test('lump sum during a deal still shortens the term after the deal ends', () => {
  const d = { loan: 5_000_000, termYears: 20, dealRate: 8.5, dealYears: 1, svr: 8.5 };
  const c = compare(d, { lumpSum: 500_000, lumpSumMonth: 6 });
  assert.ok(c.monthsSaved > 12);
  near(c.withPrepayment.monthlyPayment, c.baseline.monthlyPayment, 0.01, 'payment kept');
});

test('monthly extra keeps the reverted payment', () => {
  const d = { loan: 250_000, termYears: 25, dealRate: 4.5, dealYears: 5, svr: 7.25 };
  const c = compare(d, { monthlyExtra: 200 });
  near(c.withPrepayment.monthlyPayment, c.baseline.monthlyPayment, 0.01, 'payment kept');
  assert.ok(c.monthsSaved > 0);
});

test('reduce payment lump sum during a deal lowers payment and keeps term', () => {
  const d = { loan: 5_000_000, termYears: 20, dealRate: 8.5, dealYears: 1, svr: 8.5 };
  const c = compare(d, { lumpSum: 500_000, lumpSumMonth: 6, mode: MODE.reduceEMI });
  assert.equal(c.withPrepayment.months, c.baseline.months);
  assert.ok(c.withPrepayment.monthlyPayment < c.baseline.monthlyPayment);
});

test('reduce tenure beats reduce payment when the deal ends after the prepayment', () => {
  const d = { loan: 300_000, termYears: 25, dealRate: 4, dealYears: 2, svr: 6 };
  const t = compare(d, { lumpSum: 30_000, lumpSumMonth: 6 });
  const e = compare(d, { lumpSum: 30_000, lumpSumMonth: 6, mode: MODE.reduceEMI });
  assert.ok(t.interestSaved > e.interestSaved);
});

// Guide-page tools
test('allowance: 10% of £200k, £5k used, 6 months left', () => {
  const a = allowance({ balance: 200_000, allowancePercent: 10, overpaidSoFar: 5_000, monthsLeft: 6, ercPercent: 3 });
  near(a.yearly, 20_000, 0.001, 'yearly');
  near(a.remaining, 15_000, 0.001, 'remaining');
  near(a.perMonthLeft, 2_500, 0.001, 'per month');
  assert.equal(a.overBy, 0);
});

test('allowance: charge only on the amount over the limit', () => {
  const a = allowance({ balance: 100_000, allowancePercent: 10, overpaidSoFar: 12_000, monthsLeft: 12, ercPercent: 2 });
  near(a.remaining, 0, 0.001, 'remaining');
  near(a.overBy, 2_000, 0.001, 'over');
  near(a.ercOnOver, 40, 0.001, 'charge');
});

test('deal end: SVR payment is higher and a new deal sits between', () => {
  const e = dealEnd({ balance: 200_000, yearsLeft: 20, currentRate: 2, svr: 7.5, newRate: 4.5 });
  assert.equal(e.months, 240);
  near(e.current, 1011.77, 0.01, 'current'); // standard formula, £200k, 2%, 240 months
  assert.ok(e.svr > e.newDeal && e.newDeal > e.current);
  near(e.svrVsNewPerYear, (e.svr - e.newDeal) * 12, 0.001, 'per year');
});

test('future value with zero rate is the sum paid in', () => {
  assert.equal(futureValue(100, 0, 12), 1200);
});

test('overpay or save: picks the higher after-tax rate', () => {
  const a = overpayOrSave({ monthly: 200, years: 5, mortgageRate: 5, savingsRate: 4.5, taxRate: 20 });
  assert.equal(a.winner, 'overpay');
  const b = overpayOrSave({ monthly: 200, years: 5, mortgageRate: 3, savingsRate: 5, taxRate: 0 });
  assert.equal(b.winner, 'save');
  near(b.paidIn, 12_000, 0.001, 'paid in');
});
