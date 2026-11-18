// node --test apptools.test.mjs
// Ports of MortgageAppTests/UKPropertyCalculatorsTests.swift and the fix-length
// and early-exit cases of RemortgageCalculatorTests.swift.
import test from 'node:test';
import assert from 'node:assert/strict';
import { stampDuty, BUYER, affordability, loanToValue } from './property.js';
import { compareFixLengths, compareEarlyExit } from './remortgage.js';

const near = (a, b, tol, msg = '') => assert.ok(Math.abs(a - b) <= tol, `${msg} ${a} vs ${b}`);

test('home mover at £300k', () => assert.equal(stampDuty(300_000, BUYER.homeMover).total, 5_000));
test('home mover at £125k pays nothing', () => assert.equal(stampDuty(125_000, BUYER.homeMover).total, 0));
test('first-time buyer at £300k pays nothing', () => {
  const r = stampDuty(300_000, BUYER.firstTimeBuyer);
  assert.equal(r.total, 0);
  assert.ok(r.reliefApplied);
});
test('first-time buyer at £450k', () => assert.equal(stampDuty(450_000, BUYER.firstTimeBuyer).total, 7_500));
test('first-time buyer over £500k pays standard rates', () => {
  const r = stampDuty(550_000, BUYER.firstTimeBuyer);
  assert.ok(!r.reliefApplied && r.reliefUnavailable);
  assert.equal(r.total, 17_500);
});
test('additional property adds 5%', () => assert.equal(stampDuty(300_000, BUYER.additionalProperty).total, 20_000));
test('additional property under £40k has no surcharge', () => assert.equal(stampDuty(39_000, BUYER.additionalProperty).total, 0));
test('non-resident adds 2%', () => assert.equal(stampDuty(300_000, BUYER.homeMover, true).total, 11_000));
test('top bands', () => assert.equal(stampDuty(2_000_000, BUYER.homeMover).total, 153_750));

test('affordability uses combined income', () => {
  const r = affordability([40_000, 20_000], 30_000);
  assert.equal(r.totalIncome, 60_000);
  assert.equal(r.lowLoan, 240_000);
  assert.equal(r.typicalLoan, 270_000);
  assert.equal(r.highLoan, 330_000);
  assert.equal(r.typicalPrice, 300_000);
  near(r.typicalLTV, 90, 0.001);
});

test('LTV band and gap to the next band', () => {
  const r = loanToValue(240_000, 300_000);
  near(r.percent, 80, 0.001);
  assert.equal(r.band, 80);
  assert.equal(r.nextLowerBand, 75);
  near(r.reductionToNextBand, 15_000, 0.01);
});
test('LTV over 95% has no band', () => {
  const r = loanToValue(290_000, 300_000);
  assert.equal(r.band, null);
  assert.equal(r.nextLowerBand, 95);
});
test('LTV needs a value', () => assert.equal(loanToValue(100_000, 0), null));

test('break-even re-fix rate equalises costs', () => {
  const shorter = { rate: 4.0, years: 2, fees: 999 };
  const longer = { rate: 4.5, years: 5, fees: 999 };
  const r = compareFixLengths(200_000, 300, shorter, longer, 5.0, 999);
  assert.equal(r.horizonMonths, 60);
  assert.ok(r.breakEvenRefixRate > 4.5 && r.breakEvenRefixRate < 6);
  const at = compareFixLengths(200_000, 300, shorter, longer, r.breakEvenRefixRate, 999);
  near(at.shorterCostsMoreBy, 0, 50);
});
test('higher re-fix rate favours the longer fix', () => {
  const s = { rate: 4.0, years: 2 }, l = { rate: 4.5, years: 5 };
  assert.ok(compareFixLengths(200_000, 300, s, l, 3).shorterCostsMoreBy < 0);
  assert.ok(compareFixLengths(200_000, 300, s, l, 7).shorterCostsMoreBy > 0);
});
test('early repayment charge is a percent of the balance', () => {
  const r = compareEarlyExit(200_000, 300, 5.5, 18, 3, 4.2, 999);
  near(r.earlyRepaymentCharge, 6_000, 0.01);
  assert.ok(r.savingFromLeaving < 0);
});
test('leaving pays off when the charge is small', () => {
  assert.ok(compareEarlyExit(200_000, 300, 6.5, 36, 1, 4.0, 0).savingFromLeaving > 0);
});
