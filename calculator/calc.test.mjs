// Mirrors MortgageAppTests/MortgageCalculatorTests.swift so the web engine is
// held to the same expectations as the app. Run: node --test calc.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { standardPayments, withOverpayment, schedule, byYear, calculate, validate, maxMonthlyOverpayment } from './calc.js';

const loan = (o = {}) => ({ loan: 250000, termYears: 25, dealRate: 4.5, dealYears: 25, svr: 4.5, overpayment: 0, ...o });
const near = (a, b, tol, msg) => assert.ok(Math.abs(a - b) <= tol, `${msg}: ${a} vs ${b}`);

test('basic monthly payment (£250k, 4.5%, 25y ≈ £1,389.58)', () => {
  const r = standardPayments(loan());
  assert.equal(r.dealPayment, 1389.58);
  assert.ok(r.totalPayable > 250000);
});

test('higher rate increases payment', () => {
  assert.ok(standardPayments(loan({ dealRate: 6, svr: 6 })).dealPayment > standardPayments(loan({ dealRate: 4, svr: 4 })).dealPayment);
});

test('longer term lowers payment but raises total', () => {
  const s = standardPayments(loan({ termYears: 15, dealYears: 15 }));
  const l = standardPayments(loan({ termYears: 30, dealYears: 30 }));
  assert.ok(l.dealPayment < s.dealPayment);
  assert.ok(l.totalPayable > s.totalPayable);
});

test('two-rate period: payment rises after the deal', () => {
  const r = standardPayments(loan({ dealYears: 2, svr: 7.5 }));
  assert.ok(r.dealPayment < r.svrPayment && r.svrPayment > 0);
});

test('overpayment reduces total cost and term', () => {
  const d = loan({ overpayment: 200 });
  const std = standardPayments(d);
  const o = withOverpayment(d, std);
  assert.ok(o.totalPaid < std.totalPayable);
  assert.ok(o.saving > 0);
  assert.ok(o.years < 25);
});

test('£500/month overpayment saves at least 3 years', () => {
  const d = loan({ overpayment: 500 });
  const o = withOverpayment(d, standardPayments(d));
  assert.ok(25 - o.years > 3, `saved ${25 - o.years}y`);
});

test('schedule: length, first row and final balance', () => {
  const d = loan({ dealYears: 2, svr: 7.5 });
  const rows = schedule(d, standardPayments(d), false);
  assert.ok(rows.length >= 295 && rows.length <= 310, `rows ${rows.length}`);
  assert.equal(rows[0].month, 1);
  assert.equal(rows[0].year, 1);
  near(rows[0].opening, 250000, 0.01, 'opening');
  near(rows.at(-1).closing, 0, 1, 'final balance');
});

test('schedule with overpayment is shorter and records the overpayment', () => {
  const d = loan({ overpayment: 200 });
  const rows = schedule(d, standardPayments(d), true);
  assert.ok(rows.length < 300 && rows.length > 0);
  assert.ok(rows.some((r) => r.overpayment > 0));
});

test('schedule tracks the deal period and rates', () => {
  const d = loan({ dealYears: 2, svr: 7.5 });
  const rows = schedule(d, standardPayments(d), false);
  assert.equal(rows.filter((r) => r.inDeal).length, 24);
  assert.equal(rows[0].rate, 4.5);
  assert.equal(rows[24].rate, 7.5);
});

test('summary with overpayment shows a saving', () => {
  const r = calculate(loan({ dealYears: 2, svr: 7.5, overpayment: 200 }));
  assert.deepEqual(r.errors, {});
  assert.ok(r.over && r.over.saving > 0);
});

test('very small and very large loans calculate', () => {
  assert.ok(standardPayments(loan({ loan: 10000, termYears: 10, dealYears: 10, dealRate: 5, svr: 5 })).dealPayment > 0);
  assert.ok(standardPayments(loan({ loan: 5000000, termYears: 30, dealYears: 30, dealRate: 4, svr: 4 })).dealPayment > 0);
});

// Web-only checks
test('0% interest divides evenly', () => {
  assert.equal(standardPayments(loan({ dealRate: 0, svr: 0 })).dealPayment, 250000 / 300);
});

test('yearly roll-up interest matches total interest within pennies', () => {
  const d = loan({ dealYears: 2, svr: 7.5 });
  const std = standardPayments(d);
  const interest = byYear(schedule(d, std, false)).reduce((s, y) => s + y.interest, 0);
  near(interest, std.totalInterest, 5, 'interest');
});

test('overpayment cap is 10% of the loan a year and is flagged, not blocked', () => {
  assert.equal(maxMonthlyOverpayment(240000), 2000);
  const d = loan({ loan: 240000, overpayment: 2500 });
  const o = withOverpayment(d, standardPayments(d));
  assert.equal(o.overCap, true);
  assert.equal(withOverpayment(loan({ loan: 240000, overpayment: 2000 }), standardPayments(loan({ loan: 240000 }))).overCap, false);
});

test('validation rejects a deal longer than the term', () => {
  assert.ok(validate(loan({ dealYears: 30 })).dealYears);
  assert.deepEqual(validate(loan()), {});
});
