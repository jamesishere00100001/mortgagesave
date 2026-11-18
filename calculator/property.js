// Stamp duty (England and Northern Ireland), affordability and loan-to-value.
// A port of MortgageApp/Services/UKPropertyCalculators.swift so the web pages and
// the app give the same figures. Bands are the rates in force from 1 April 2025
// (GOV.UK "Stamp Duty Land Tax: residential property rates"). Change them in both.

export const BUYER = { homeMover: 'homeMover', firstTimeBuyer: 'firstTimeBuyer', additionalProperty: 'additionalProperty' };

export const STANDARD_BANDS = [
  { from: 0, to: 125_000, rate: 0 },
  { from: 125_000, to: 250_000, rate: 2 },
  { from: 250_000, to: 925_000, rate: 5 },
  { from: 925_000, to: 1_500_000, rate: 10 },
  { from: 1_500_000, to: null, rate: 12 },
];
export const FIRST_TIME_BUYER_BANDS = [
  { from: 0, to: 300_000, rate: 0 },
  { from: 300_000, to: 500_000, rate: 5 },
];
export const FIRST_TIME_BUYER_PRICE_LIMIT = 500_000;
export const ADDITIONAL_PROPERTY_SURCHARGE = 5;
export const ADDITIONAL_PROPERTY_MINIMUM_PRICE = 40_000;
export const NON_RESIDENT_SURCHARGE = 2;

export function stampDuty(price, buyer, nonUKResident = false) {
  if (!(price > 0)) return { price: 0, total: 0, breakdown: [], reliefApplied: false, reliefUnavailable: false, effectiveRate: 0 };
  const reliefApplies = buyer === BUYER.firstTimeBuyer && price <= FIRST_TIME_BUYER_PRICE_LIMIT;
  let surcharge = nonUKResident ? NON_RESIDENT_SURCHARGE : 0;
  if (buyer === BUYER.additionalProperty && price >= ADDITIONAL_PROPERTY_MINIMUM_PRICE) surcharge += ADDITIONAL_PROPERTY_SURCHARGE;

  const bands = reliefApplies ? FIRST_TIME_BUYER_BANDS : STANDARD_BANDS;
  const breakdown = [];
  for (const band of bands) {
    if (!(price > band.from)) continue;
    const upper = band.to == null ? price : Math.min(price, band.to);
    const taxable = upper - band.from;
    const rate = band.rate + surcharge;
    breakdown.push({ from: band.from, to: band.to, rate, taxable, tax: (taxable * rate) / 100 });
  }
  const total = Math.floor(breakdown.reduce((s, b) => s + b.tax, 0));
  return {
    price,
    total,
    breakdown,
    reliefApplied: reliefApplies,
    reliefUnavailable: buyer === BUYER.firstTimeBuyer && !reliefApplies,
    effectiveRate: (total / price) * 100,
  };
}

export const LOW_MULTIPLE = 4.0;
export const TYPICAL_MULTIPLE = 4.5;
export const HIGH_MULTIPLE = 5.5;

export function affordability(incomes, deposit, multiple = TYPICAL_MULTIPLE) {
  const income = incomes.filter((x) => x > 0).reduce((a, b) => a + b, 0);
  const dep = Math.max(0, deposit);
  const typicalLoan = income * multiple;
  const typicalPrice = typicalLoan + dep;
  return {
    totalIncome: income,
    lowLoan: income * LOW_MULTIPLE,
    typicalLoan,
    highLoan: income * HIGH_MULTIPLE,
    deposit: dep,
    typicalPrice,
    typicalLTV: ltvPercent(typicalLoan, typicalPrice),
  };
}

export const LTV_BANDS = [60, 75, 80, 85, 90, 95];

export function ltvPercent(loan, value) {
  if (!(value > 0) || !(loan >= 0)) return null;
  return (loan / value) * 100;
}

export function loanToValue(loan, propertyValue) {
  const percent = ltvPercent(loan, propertyValue);
  if (percent == null) return null;
  const band = LTV_BANDS.find((b) => percent <= b + 1e-9) ?? null;
  let lower = null;
  if (band != null) {
    const i = LTV_BANDS.indexOf(band);
    if (i > 0) lower = LTV_BANDS[i - 1];
  } else {
    lower = LTV_BANDS.at(-1);
  }
  const reduction = lower == null ? null : Math.max(0, loan - (propertyValue * lower) / 100);
  return { percent, band, nextLowerBand: lower, reductionToNextBand: reduction };
}
