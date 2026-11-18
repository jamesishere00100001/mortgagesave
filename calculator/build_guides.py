# Generates the guide pages (one folder each) from the PAGES list below.
# Optional: the pages are plain static HTML, so small edits can be made by hand,
# but re-running this overwrites them. Run from anywhere: python3 build_guides.py
import json, os, html
OUT = os.path.dirname(os.path.abspath(__file__))
BASE = 'https://mortgagesave.very-good-studio.com'
APP = 'https://apps.apple.com/app/id6467675017'
HOUSE = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M4 11.5 12 5l8 6.5V20a1 1 0 0 1-1 1h-4.5v-5.5h-5V21H5a1 1 0 0 1-1-1v-8.5Z" fill="#E8E6FF"/></svg>'

# What the app does, as listed on every guide page. Only name features in the live App Store version.
APP_FEATURES = ''.join(f'\n            <li>{x}</li>' for x in [
    'Save scenarios and compare up to three side by side',
    'A reminder before your deal reverts to the SVR',
    'Full month-by-month schedule and PDF export',
]) + '\n          '

PAGES = []  # filled below; also used for "related" links

def field(id, label, kind='num', hint=None, options=None):
    if kind == 'select':
        opts = ''.join(f'<option value="{v}">{html.escape(t)}</option>' for v, t in options)
        box = f'<div class="box"><select id="{id}" name="{id}">{opts}</select></div>'
    else:
        pre = '<span>£</span>' if kind == 'money' else ''
        post = '<span class="after">%</span>' if kind == 'pct' else ('<span class="after">yrs</span>' if kind == 'yrs' else '')
        box = f'<div class="box">{pre}<input id="{id}" name="{id}" inputmode="decimal" autocomplete="off">{post}</div>'
    h = f'<div class="hint">{hint}</div>' if hint else ''
    return f'''<div class="field" id="f-{id}">
              <label for="{id}">{label}</label>
              {box}{h}
              <div class="err" id="e-{id}"></div>
            </div>'''

def pair(a, b):
    return f'<div class="pair">\n            {a}\n            {b}\n          </div>'

def page(p):
    url = f"{BASE}/{p['slug']}/"
    faq = {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p['faq']]}
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebApplication", "name": p['h1'], "url": url, "inLanguage": "en-GB",
         "applicationCategory": "FinanceApplication", "operatingSystem": "Any",
         "offers": {"@type": "Offer", "price": "0", "priceCurrency": "GBP"},
         "description": p['desc'], "publisher": {"@id": "https://very-good-studio.com/#org"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Mortgage overpayment calculator", "item": BASE + "/"},
            {"@type": "ListItem", "position": 2, "name": p['h1'], "item": url}]},
        faq,
        {"@type": "Organization", "@id": "https://very-good-studio.com/#org", "name": "Very Good Studio", "url": "https://very-good-studio.com/"}]}
    related = ''.join(
        f'<li><a href="../{o["slug"]}/">{o["h1"]}<span>{o["short"]}</span></a></li>'
        for o in PAGES if o is not p)
    related = f'<li><a href="../">Mortgage overpayment calculator<span>Monthly overpayments across your deal and the SVR</span></a></li>' + related
    faq_html = ''.join(f'<h2>{html.escape(q)}</h2>\n<p>{html.escape(a)}</p>\n' for q, a in p['faq'])
    return f'''<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{p['title']}</title>
<meta name="description" content="{p['desc']}">
<meta name="apple-itunes-app" content="app-id=6467675017">
<link rel="canonical" href="{url}">
<link rel="icon" href="../favicon.png" type="image/png">
<link rel="apple-touch-icon" href="../apple-touch-icon.png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Mortgage Save">
<meta property="og:locale" content="en_GB">
<meta property="og:title" content="{p['h1']} – Mortgage Save">
<meta property="og:description" content="{p['desc']}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope:wght@600;700;800&family=Inter:wght@400;500;600&display=swap">
<link rel="stylesheet" href="../site.css">
<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=2)}
</script>
</head>
<body>
<header class="top">
  <div class="wrap">
    <div class="brandline">
      <a class="brand" href="../">
        <span class="brand-mark" aria-hidden="true">
          {HOUSE}
        </span>
        Mortgage Save
      </a>
      <a class="store-link" href="{APP}" rel="noopener">Get the iPhone app</a>
    </div>
    <div>
      <nav class="crumbs" aria-label="Breadcrumb"><a href="../">Overpayment calculator</a> › {p['crumb']}</nav>
      <h1>{p['h1']}</h1>
      <p class="lede">{p['lede']}</p>
    </div>
  </div>
</header>

<main>
  <div class="wrap">
    <div class="calc">
      <form class="panel inputs-panel" id="form" novalidate>
        <h2>{p['form_title']}</h2>
        <div class="inputs">
          {p['form']}
          <div class="example-note"><span>Example figures. Change them to yours. They stay in this browser.</span></div>
        </div>
      </form>

      <div class="results">
        {p['results']}

        <section class="panel app">
          <h2>Mortgage Save for iPhone</h2>
          <p class="pitch">{p['pitch']}</p>
          <ul>{APP_FEATURES}</ul>
          <a class="cta" href="{APP}" rel="noopener">Download on the App Store</a>
        </section>
      </div>
    </div>

    <article class="article">
      {p['article']}
      {faq_html}
    </article>

    <nav class="related" aria-label="More calculators">
      <h2>More mortgage calculators</h2>
      <ul>{related}</ul>
    </nav>
  </div>
</main>

<footer>
  <div class="wrap">
    <span>Figures are estimates for guidance only and aren’t financial advice. Your lender’s statement is the final word. Interest is calculated monthly at the rates you enter.</span>
    <span>Everything you type stays in your browser. Nothing is sent or stored. <a href="https://very-good-studio.com/apps/mortgage-save/privacy-policy.html">Privacy policy</a></span>
  </div>
</footer>

<script type="module">
{p['script'].strip()}
</script>
<!-- Cloudflare Web Analytics --><script type='module' src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{{"token": "3850486203cd40769943ba21bf3ae65b"}}'></script><!-- End Cloudflare Web Analytics -->
</body>
</html>
'''

# ---------- 1. Lump sum ----------
PAGES.append(dict(
  slug='lump-sum-overpayment-calculator',
  title='Lump Sum Mortgage Overpayment Calculator UK | Mortgage Save',
  desc='Free UK calculator: see how much interest a one-off lump sum overpayment saves, how much sooner you’d be mortgage-free, or how far your monthly payment would drop. Includes early repayment charges.',
  h1='Lump sum mortgage overpayment calculator',
  short='A one-off payment: interest and time saved',
  crumb='Lump sum',
  lede='Paying off a chunk of your mortgage in one go? See the interest it saves, and whether to finish sooner or lower your monthly payment.',
  form_title='Your mortgage today',
  form='\n          '.join([
    pair(field('balance', 'Balance owed now', 'money'), field('yearsLeft', 'Years left', 'yrs')),
    pair(field('dealRate', 'Rate now', 'pct'), field('dealYearsLeft', 'Years left on deal', 'yrs', 'Enter 0 if you’re on the SVR')),
    field('svr', 'Rate after the deal (SVR)', 'pct'),
    '<div class="group">' + pair(field('lumpSum', 'Lump sum', 'money'), field('month', 'Paid in month', 'num', '1 = next month')),
    field('erc', 'Early repayment charge', 'pct', 'Charged on the lump sum during your deal. Use 0 if it’s within your allowance.'),
    field('mode', 'Afterwards', 'select', None, [('reduceTenure', 'Keep the payment, finish sooner'), ('reduceEMI', 'Lower the payment, same end date')]) + '</div>',
  ]),
  results='''<section class="panel saving" id="savingPanel">
          <h2>What the lump sum saves</h2>
          <div id="out"></div>
        </section>
        <section class="panel">
          <h2>Before and after</h2>
          <div class="stats" style="margin-top:0">
            <div class="stat"><span class="k">Monthly payment now</span><span class="v" id="s-pay">–</span></div>
            <div class="stat"><span class="k" id="s-after-k">Payment afterwards</span><span class="v" id="s-after">–</span></div>
            <div class="stat"><span class="k">Mortgage-free in</span><span class="v" id="s-term">–</span></div>
            <div class="stat"><span class="k">Interest left to pay</span><span class="v" id="s-int">–</span></div>
          </div>
          <p class="fullcalc">Thinking of overpaying every month instead? <a href="../" id="full">Try the monthly overpayment calculator</a>.</p>
        </section>''',
  pitch='Save this scenario, compare it with overpaying monthly, and get reminded before your deal ends.',
  article='''<h2>How a lump sum overpayment works</h2>
<p>A lump sum goes straight off your balance, so every month after it you pay interest on a smaller amount. This calculator follows your mortgage month by month: your current rate until your deal ends, then the rate after it, with the lump sum paid in the month you choose.</p>
<h2>Finish sooner or pay less each month?</h2>
<p>After an overpayment, most UK lenders either keep your monthly payment the same, so the mortgage ends earlier, or recalculate it lower over the same term. Keeping the payment the same saves more interest, because the balance falls faster. Lowering the payment frees up money each month, which can matter more if your budget is tight. Your lender will usually let you choose, but some pick one by default, so ask.</p>
<h2>Watch the 10% limit during a fixed deal</h2>
<p>Most fixed and tracker deals let you overpay up to 10% of your balance a year without a charge. A lump sum counts towards that, along with any regular overpayments. Above it, an early repayment charge (often 1% to 5%, falling each year of the deal) applies to the extra. The <a href="../mortgage-overpayment-allowance-calculator/">overpayment allowance calculator</a> shows how much you can still pay this year. Waiting until the deal ends, when there’s normally no limit, can avoid the charge altogether.</p>
<h2>Before you pay a lump sum</h2>
<ul>
<li>Keep an emergency fund. Money paid off a mortgage is hard to get back.</li>
<li>Pay off dearer debts, like credit cards or car finance, first.</li>
<li>If you’re close to a lower loan-to-value band (say 75% or 60%), a lump sum before you remortgage can get you a better rate as well.</li>
</ul>''',
  faq=[
    ('Is it better to pay a lump sum off the mortgage or overpay monthly?', 'The same total saves more interest when it is paid sooner, so a lump sum now beats spreading it over the year. Monthly overpayments are easier to fit around a budget and to keep within the 10% allowance.'),
    ('Do I have to tell my lender about a lump sum overpayment?', 'Usually yes. Many lenders want you to pay it by bank transfer or debit card through their website or app and to say whether to reduce your term or your payment.'),
    ('Does a lump sum reduce my monthly payment?', 'It depends on your lender. Some lower the payment automatically and some keep it the same and shorten the term. You can normally ask for either.'),
  ],
  script='''
import { setup, $, gbp0, gbp2, duration, fullCalculatorLink } from '../guide.js';
import { compare } from '../simulator.js';
import { OVERPAYMENT_CAP_PERCENT } from '../calc.js';

setup({
  fields: {
    balance: { min: 1000, max: 10000000, money: true },
    yearsLeft: { min: 1, max: 50 },
    dealRate: { min: 0, max: 25 },
    dealYearsLeft: { min: 0, max: 50 },
    svr: { min: 0, max: 25 },
    lumpSum: { min: 1, max: 10000000, money: true },
    month: { min: 1, max: 600 },
    erc: { min: 0, max: 10 },
    mode: { text: true },
  },
  defaults: { balance: 200000, yearsLeft: 22, dealRate: 4.5, dealYearsLeft: 3, svr: 7.25, lumpSum: 10000, month: 1, erc: 0, mode: 'reduceTenure' },
  check: (d) => {
    const e = {};
    if (d.dealYearsLeft > d.yearsLeft) e.dealYearsLeft = 'The deal can’t run past the end of the mortgage';
    if (d.lumpSum >= d.balance) e.lumpSum = 'That would clear the mortgage. Enter less than the balance.';
    if (d.month > d.yearsLeft * 12) e.month = 'That’s after the mortgage ends';
    return e;
  },
  showInvalid: () => { $('out').innerHTML = '<p class="empty-over">Check the figures marked in red.</p>'; },
  render: (d) => {
    const loan = { loan: d.balance, termYears: d.yearsLeft, dealRate: d.dealRate, dealYears: d.dealYearsLeft, svr: d.svr };
    const c = compare(loan, { lumpSum: d.lumpSum, lumpSumMonth: d.month, ercPercent: d.erc, mode: d.mode });
    if (!c) { $('out').innerHTML = '<p class="empty-over">These figures don’t work out. Check the rates and term.</p>'; return; }
    const b = c.baseline, w = c.withPrepayment;
    const tenure = d.mode === 'reduceTenure';
    const inDeal = d.month <= d.dealYearsLeft * 12;
    const overAllowance = inDeal && d.lumpSum > d.balance * OVERPAYMENT_CAP_PERCENT / 100;
    $('out').innerHTML = `
      <div class="saving-grid">
        <div><div class="big">${gbp0.format(Math.max(0, c.interestSaved))}</div><div class="k">less interest</div></div>
        <div><div class="big">${tenure ? duration(Math.max(0, c.monthsSaved)) : gbp2.format(Math.max(0, b.monthlyPayment - w.monthlyPayment))}</div><div class="k">${tenure ? 'sooner mortgage-free' : 'less a month by the end'}</div></div>
      </div>
      <p>${w.totalCharges > 0 ? `After an early repayment charge of ${gbp0.format(w.totalCharges)}, you’d be ${gbp0.format(c.netSaving)} better off overall.` : `Paying ${gbp0.format(d.lumpSum)} in month ${d.month} ${tenure ? `clears the mortgage in ${duration(w.months)} instead of ${duration(b.months)}` : 'keeps the same end date with a lower payment'}.`}</p>
      ${overAllowance && d.erc === 0 ? `<div class="callout">This is more than ${OVERPAYMENT_CAP_PERCENT}% of your balance (${gbp0.format(d.balance * OVERPAYMENT_CAP_PERCENT / 100)}) during your deal. Most lenders charge an early repayment charge on the extra. Add your charge above to include it.</div>` : ''}
      <p class="nudge">Want a reminder before your deal ends, when there’s usually no limit? <a href="https://apps.apple.com/app/id6467675017" rel="noopener">Mortgage Save for iPhone</a> can do that.</p>`;
    $('s-pay').textContent = gbp2.format(b.monthlyPayment);
    $('s-after-k').textContent = tenure ? 'Payment afterwards' : 'Payment after the lump sum';
    $('s-after').textContent = gbp2.format(w.monthlyPayment);
    $('s-term').textContent = duration(w.months);
    $('s-int').textContent = gbp0.format(w.totalInterest);
    $('full').href = fullCalculatorLink({ loan: d.balance, termYears: d.yearsLeft, dealRate: d.dealRate, dealYears: Math.max(d.dealYearsLeft, 1), svr: d.svr, overpayment: Math.round(d.lumpSum / 12) });
  },
});
'''))

# ---------- 2. Allowance ----------
PAGES.append(dict(
  slug='mortgage-overpayment-allowance-calculator',
  title='Mortgage Overpayment Allowance Calculator: the 10% Rule | Mortgage Save',
  desc='How much can you overpay your mortgage without a penalty? Work out your 10% overpayment allowance, what’s left this year, and the early repayment charge on anything over it.',
  h1='How much can I overpay my mortgage?',
  short='Your 10% allowance and any charge over it',
  crumb='Overpayment allowance',
  lede='Work out your penalty-free overpayment allowance for this year, how much of it is left, and what you’d pay in charges if you go over.',
  form_title='Your allowance',
  form='\n          '.join([
    field('balance', 'Balance your lender measures from', 'money', 'Usually the balance at the start of your mortgage year. Some lenders use the original loan.'),
    pair(field('pct', 'Allowance each year', 'pct'), field('used', 'Overpaid so far this year', 'money')),
    pair(field('monthsLeft', 'Months left in year', 'num'), field('erc', 'Repayment charge', 'pct')),
  ]),
  results='''<section class="panel saving">
          <h2>Left to overpay this year</h2>
          <div id="out"></div>
        </section>
        <section class="panel">
          <h2>Your allowance</h2>
          <div class="stats" style="margin-top:0">
            <div class="stat"><span class="k">Allowance this year</span><span class="v" id="s-year">–</span></div>
            <div class="stat"><span class="k">Spread evenly, a month</span><span class="v" id="s-even">–</span></div>
            <div class="stat"><span class="k">Used so far</span><span class="v" id="s-used">–</span></div>
          </div>
          <p class="fullcalc">See what overpaying this much saves in the <a href="../" id="full">overpayment calculator</a>.</p>
        </section>''',
  pitch='Keep your figures in one place and get reminded before your deal ends, when the limit usually lifts.',
  article='''<h2>The 10% overpayment rule</h2>
<p>Most UK fixed and tracker deals let you overpay up to 10% of your balance each year without an early repayment charge (ERC). It’s a lender rule rather than a law, so the details vary:</p>
<ul>
<li><strong>What the 10% is of.</strong> Most lenders use the balance at the start of each year of the deal. A few use the original loan, or the balance on the day you overpay.</li>
<li><strong>When the year resets.</strong> Often on your deal’s anniversary, sometimes on 1 January.</li>
<li><strong>What counts.</strong> Regular monthly overpayments and one-off lump sums usually share the same allowance.</li>
<li><strong>Unused allowance.</strong> It rarely carries over to the next year.</li>
</ul>
<p>Your mortgage offer or your lender’s app will say which applies to you.</p>
<h2>What happens if you overpay more than 10%?</h2>
<p>The ERC is charged on the amount over the allowance, not on the whole overpayment. Charges are usually 1% to 5% and step down each year of the deal, so going over late in a deal costs less. Once your deal ends and you move to the standard variable rate, there’s normally no limit and no charge.</p>
<h2>Turning the allowance into a monthly figure</h2>
<p>Dividing the allowance by twelve gives the largest regular overpayment you can make all year without going over. If you’ve already overpaid this year, the calculator spreads what’s left over the remaining months.</p>''',
  faq=[
    ('Can I overpay my mortgage by more than 10%?', 'Yes, but during a fixed or tracker deal most lenders charge an early repayment charge on the amount above the allowance. On the standard variable rate there is usually no limit.'),
    ('Is the 10% overpayment allowance per year or for the whole deal?', 'It is per year of the deal with most lenders, and unused allowance usually does not carry over.'),
    ('Does a lump sum count towards the 10% allowance?', 'Yes. Regular overpayments and one-off lump sums normally share the same yearly allowance.'),
  ],
  script='''
import { setup, $, gbp0, gbp2, plain } from '../guide.js';
import { allowance } from '../tools.js';

setup({
  fields: {
    balance: { min: 1000, max: 10000000, money: true },
    pct: { min: 0, max: 100 },
    used: { min: 0, max: 10000000, money: true },
    monthsLeft: { min: 1, max: 12, msg: 'Enter 1 to 12 months' },
    erc: { min: 0, max: 10 },
  },
  defaults: { balance: 180000, pct: 10, used: 2000, monthsLeft: 7, erc: 3 },
  showInvalid: () => { $('out').innerHTML = '<p class="empty-over">Check the figures marked in red.</p>'; },
  render: (d) => {
    const a = allowance({ balance: d.balance, allowancePercent: d.pct, overpaidSoFar: d.used, monthsLeft: d.monthsLeft, ercPercent: d.erc });
    $('out').innerHTML = a.overBy > 0 ? `
      <div class="saving-grid"><div><div class="big">£0</div><div class="k">left this year</div></div></div>
      <div class="callout">You’re ${gbp0.format(a.overBy)} over your allowance. At ${plain(d.erc)}%, that’s an early repayment charge of about ${gbp2.format(a.ercOnOver)}.</div>` : `
      <div class="saving-grid">
        <div><div class="big">${gbp0.format(a.remaining)}</div><div class="k">left this year</div></div>
        <div><div class="big">${gbp0.format(a.perMonthLeft)}</div><div class="k">a month for the next ${d.monthsLeft} month${d.monthsLeft === 1 ? '' : 's'}</div></div>
      </div>
      <p>Going over would cost ${plain(d.erc)}% of the extra: ${gbp2.format(d.erc * 10)} for every £1,000 above the limit.</p>`;
    $('out').innerHTML += `<p class="nudge">The limit usually lifts when your deal ends. <a href="https://apps.apple.com/app/id6467675017" rel="noopener">Mortgage Save for iPhone</a> can remind you before then.</p>`;
    $('s-year').textContent = gbp0.format(a.yearly);
    $('s-even').textContent = gbp0.format(a.monthlyEven);
    $('s-used').textContent = gbp0.format(d.used);
  },
});
'''))

# ---------- 3. Fixed rate ending ----------
PAGES.append(dict(
  slug='fixed-rate-ending-calculator',
  title='Fixed Rate Ending Calculator: Your Payment on the SVR vs a New Deal | Mortgage Save',
  desc='Is your fixed rate mortgage ending? See your new monthly payment on your lender’s standard variable rate, on a new deal, and what a year of doing nothing would cost.',
  h1='Fixed rate ending calculator',
  short='Your payment on the SVR vs a new deal',
  crumb='Fixed rate ending',
  lede='See what happens to your monthly payment when your fixed rate ends: on your lender’s standard variable rate, or on a new deal.',
  form_title='When your deal ends',
  form='\n          '.join([
    pair(field('balance', 'Balance when the deal ends', 'money'), field('yearsLeft', 'Years left then', 'yrs')),
    field('currentRate', 'Your current fixed rate', 'pct'),
    pair(field('svr', 'Lender’s SVR', 'pct'), field('newRate', 'New deal rate', 'pct', 'A rate you’ve been offered or seen')),
  ]),
  results='''<section class="panel">
          <h2>Your new payment</h2>
          <div class="headline"><span class="k">On the standard variable rate</span><span class="v" id="h-svr">–</span><span class="s" id="h-sub"></span></div>
          <div class="stats">
            <div class="stat"><span class="k">Payment now</span><span class="v" id="s-now">–</span></div>
            <div class="stat"><span class="k">On a new deal</span><span class="v" id="s-new">–</span></div>
            <div class="stat"><span class="k">On the SVR</span><span class="v up" id="s-svr">–</span></div>
          </div>
        </section>
        <section class="panel saving">
          <h2>Cost of doing nothing</h2>
          <div id="out"></div>
        </section>''',
  pitch='Get reminded months before your deal ends, so you never drift onto the SVR.',
  article='''<h2>What happens when a fixed rate ends</h2>
<p>When your fixed or tracker deal finishes, your lender moves you onto its standard variable rate (SVR) unless you’ve arranged something else. SVRs are usually several percentage points above the best deals, so the payment can jump by hundreds of pounds a month. This calculator works out the payment on the balance and term left, at each rate.</p>
<h2>When to start looking</h2>
<p>Most lenders let you choose a new deal with them (a product transfer) up to three to six months before your deal ends, and remortgage offers from other lenders usually last about six months. Starting early means you can lock in a rate and still switch if a better one turns up. Leaving it until after the deal ends means paying the SVR for every month it takes to arrange.</p>
<h2>Stay with your lender or switch?</h2>
<p>A product transfer is usually quicker, with no new affordability checks or valuation. Switching lender can get a lower rate but may come with legal and valuation work. Compare deals on the total cost over the fixed period, including arrangement fees, not just the rate.</p>
<h2>Overpay before you remortgage</h2>
<p>If your balance is close to a loan-to-value threshold (often 60%, 75%, 80% or 85%), overpaying before your deal ends can move you into a cheaper rate band. There’s usually no charge for overpaying once you’re on the SVR. The <a href="../">overpayment calculator</a> shows the effect.</p>''',
  faq=[
    ('What happens if I do nothing when my fixed rate ends?', 'Your lender moves you to its standard variable rate. You can usually still move to a new deal afterwards, normally without an early repayment charge, but you pay the higher rate in the meantime.'),
    ('How early can I lock in a new mortgage deal?', 'Most lenders let you choose a product transfer three to six months before your current deal ends, and many remortgage offers are valid for about six months.'),
    ('Is the SVR always higher than a new fixed rate?', 'Almost always. SVRs are set by each lender and are typically well above the rates on new fixed and tracker deals.'),
  ],
  script='''
import { setup, $, gbp0, gbp2, plain, duration, fullCalculatorLink } from '../guide.js';
import { dealEnd } from '../tools.js';

setup({
  fields: {
    balance: { min: 1000, max: 10000000, money: true },
    yearsLeft: { min: 1, max: 50 },
    currentRate: { min: 0, max: 25 },
    svr: { min: 0, max: 25 },
    newRate: { min: 0, max: 25 },
  },
  defaults: { balance: 180000, yearsLeft: 20, currentRate: 1.9, svr: 7.5, newRate: 4.4 },
  showInvalid: () => { $('out').innerHTML = '<p class="empty-over">Check the figures marked in red.</p>'; },
  render: (d) => {
    const e = dealEnd({ balance: d.balance, yearsLeft: d.yearsLeft, currentRate: d.currentRate, svr: d.svr, newRate: d.newRate });
    const sign = (x) => (x >= 0 ? '+' : '−') + gbp2.format(Math.abs(x));
    $('h-svr').textContent = gbp2.format(e.svr);
    $('h-sub').textContent = `${sign(e.svrJump)} a month compared with now, at ${plain(d.svr)}% over ${duration(e.months)}`;
    $('s-now').textContent = gbp2.format(e.current);
    $('s-new').textContent = gbp2.format(e.newDeal);
    $('s-svr').textContent = gbp2.format(e.svr);
    const full = fullCalculatorLink({ loan: d.balance, termYears: d.yearsLeft, dealRate: d.newRate, dealYears: Math.min(5, d.yearsLeft), svr: d.svr, overpayment: 0 });
    $('out').innerHTML = e.svrVsNewPerYear > 0 ? `
      <div class="saving-grid">
        <div><div class="big">${gbp0.format(e.svrVsNewPerYear)}</div><div class="k">a year extra on the SVR</div></div>
        <div><div class="big">${gbp0.format(e.svrVsNewPerYear / 12)}</div><div class="k">for every month you wait</div></div>
      </div>
      <p>That’s what staying on the ${plain(d.svr)}% SVR costs compared with a ${plain(d.newRate)}% deal. <a href="${full}">See this new deal in the overpayment calculator</a>.</p>
      <p class="nudge">Don’t miss the date. <a href="https://apps.apple.com/app/id6467675017" rel="noopener">Mortgage Save for iPhone</a> reminds you before your deal ends.</p>` : `
      <p class="empty-over">At these rates the new deal isn’t cheaper than the SVR. Check the rates you’ve entered.</p>`;
  },
});
'''))

# ---------- 4. Overpay or save ----------
PAGES.append(dict(
  slug='overpay-mortgage-or-save-calculator',
  title='Overpay Mortgage or Save? UK Calculator | Mortgage Save',
  desc='Should you overpay your mortgage or put the money in savings? Compare the interest you’d avoid by overpaying with the interest you’d earn after tax.',
  h1='Overpay your mortgage or save?',
  short='Interest saved vs interest earned after tax',
  crumb='Overpay or save',
  lede='Compare putting spare money towards your mortgage with saving it, after tax on the interest.',
  form_title='Your money',
  form='\n          '.join([
    pair(field('monthly', 'Each month', 'money'), field('years', 'For how long', 'yrs')),
    pair(field('mortgageRate', 'Mortgage rate', 'pct'), field('savingsRate', 'Savings rate', 'pct')),
    field('tax', 'Tax on savings interest', 'select', 'Most people pay no tax on savings interest within their Personal Savings Allowance or in an ISA.',
          [('0', 'None (ISA or within allowance)'), ('20', '20% (basic rate)'), ('40', '40% (higher rate)'), ('45', '45% (additional rate)')]),
  ]),
  results='''<section class="panel saving">
          <h2>Which comes out ahead</h2>
          <div id="out"></div>
        </section>
        <section class="panel">
          <h2>After the period</h2>
          <div class="stats" style="margin-top:0">
            <div class="stat"><span class="k">Paid in</span><span class="v" id="s-in">–</span></div>
            <div class="stat"><span class="k">Interest avoided by overpaying</span><span class="v" id="s-over">–</span></div>
            <div class="stat"><span class="k">Interest earned after tax</span><span class="v" id="s-save">–</span></div>
          </div>
        </section>''',
  pitch='Try both plans on your real mortgage, save them side by side, and get reminded before your deal ends.',
  article='''<h2>How the comparison works</h2>
<p>Every pound you overpay stops being charged interest at your mortgage rate, so overpaying earns you, in effect, your mortgage rate with no tax and no risk. Savings earn the account’s rate, minus any tax on the interest. The calculator compares the two over the same period, with interest added monthly, and assumes both rates stay the same.</p>
<h2>Tax on savings interest</h2>
<p>The Personal Savings Allowance lets basic-rate taxpayers earn £1,000 of interest a year tax-free and higher-rate taxpayers £500. Additional-rate taxpayers get none. Interest in an ISA is always tax-free. If your savings interest is already above your allowance, choose your tax rate above.</p>
<h2>It’s not just about the rate</h2>
<ul>
<li><strong>Access.</strong> Savings are there if you need them. Money paid off your mortgage usually isn’t, unless your mortgage allows payment holidays or borrowing back.</li>
<li><strong>Emergency fund first.</strong> Most guidance suggests keeping three to six months of spending in easy-access savings before overpaying.</li>
<li><strong>Dearer debts first.</strong> Credit cards and loans usually cost more than a mortgage.</li>
<li><strong>Remortgaging.</strong> A lower balance can move you into a cheaper loan-to-value band at your next deal.</li>
<li><strong>Allowance.</strong> During a fixed deal you can usually overpay up to 10% of the balance a year without a charge.</li>
</ul>
<p>A middle route is to save during your deal and pay a lump sum off when it ends, when there’s usually no overpayment limit. The <a href="../lump-sum-overpayment-calculator/">lump sum calculator</a> shows what that saves.</p>''',
  faq=[
    ('Is it better to overpay my mortgage or save?', 'If your savings rate after tax is lower than your mortgage rate, overpaying usually saves more. Savings are easier to get back, so many people keep an emergency fund first and overpay with what is left.'),
    ('Do I pay tax on savings interest?', 'Only above your Personal Savings Allowance: £1,000 a year for basic-rate taxpayers, £500 for higher-rate and nothing for additional-rate. ISA interest is tax-free.'),
    ('Can I get money back after overpaying my mortgage?', 'Usually not. Some flexible mortgages let you borrow back overpayments or take payment holidays, so check with your lender.'),
  ],
  script='''
import { setup, $, gbp0, plain } from '../guide.js';
import { overpayOrSave } from '../tools.js';

setup({
  fields: {
    monthly: { min: 1, max: 100000, money: true },
    years: { min: 1, max: 40 },
    mortgageRate: { min: 0, max: 25 },
    savingsRate: { min: 0, max: 25 },
    tax: { text: true },
  },
  defaults: { monthly: 200, years: 5, mortgageRate: 4.5, savingsRate: 4.25, tax: '0' },
  showInvalid: () => { $('out').innerHTML = '<p class="empty-over">Check the figures marked in red.</p>'; },
  render: (d) => {
    const r = overpayOrSave({ monthly: d.monthly, years: d.years, mortgageRate: d.mortgageRate, savingsRate: d.savingsRate, taxRate: Number(d.tax) });
    const head = r.winner === 'tie' ? 'About the same' : r.winner === 'overpay' ? 'Overpaying' : 'Saving';
    $('out').innerHTML = `
      <div class="saving-grid">
        <div><div class="big">${head}</div><div class="k">${r.winner === 'tie' ? 'either way' : `by ${gbp0.format(Math.abs(r.difference))}`}</div></div>
      </div>
      <p>Your savings would earn ${plain(+r.afterTaxSavingsRate.toFixed(2))}% after tax, against ${plain(d.mortgageRate)}% on your mortgage.${r.winner === 'save' ? ' Saving keeps the money easy to reach too.' : ''}</p>
      <p class="nudge">See what overpaying does to your mortgage-free date in the <a href="../">overpayment calculator</a>, or keep both plans in <a href="https://apps.apple.com/app/id6467675017" rel="noopener">Mortgage Save for iPhone</a>.</p>`;
    $('s-in').textContent = gbp0.format(r.paidIn);
    $('s-over').textContent = gbp0.format(r.overpayGain);
    $('s-save').textContent = gbp0.format(r.saveGain);
  },
});
'''))

# ---------- 5. Stamp duty ----------
PAGES.append(dict(
  slug='stamp-duty-calculator',
  title='Stamp Duty Calculator England 2026: First-Time Buyers and Home Movers | Mortgage Save',
  desc='Free stamp duty calculator for England and Northern Ireland at the rates from 1 April 2025. First-time buyer relief, home movers, second homes and non-UK residents, with a band-by-band breakdown.',
  h1='Stamp duty calculator',
  short='England and NI, with first-time buyer relief',
  crumb='Stamp duty',
  lede='Work out the Stamp Duty Land Tax on a home in England or Northern Ireland, at the rates in force since 1 April 2025.',
  form_title='The purchase',
  form='\n          '.join([
    field('price', 'Purchase price', 'money'),
    field('buyer', 'You are', 'select', None, [('homeMover', 'Moving home or buying your only home'), ('firstTimeBuyer', 'A first-time buyer'), ('additionalProperty', 'Buying an additional property')]),
    field('nonResident', 'Non-UK resident?', 'select', 'Adds 2% if you haven’t been in the UK for 183 days in the year before buying.', [('no', 'No'), ('yes', 'Yes')]),
  ]),
  results='''<section class="panel">
          <h2>Stamp duty to pay</h2>
          <div class="headline"><span class="k">Total</span><span class="v" id="h-total">–</span><span class="s" id="h-sub"></span></div>
          <div id="note"></div>
          <div class="table-scroll"><table id="bands"></table></div>
        </section>''',
  pitch='Plan the whole move: the mortgage payment, your deal-end date and what overpaying saves.',
  article='''<h2>How stamp duty is worked out</h2>
<p>Stamp Duty Land Tax (SDLT) is charged in bands, like income tax: each rate only applies to the part of the price inside that band. Since 1 April 2025 the rates for a home in England or Northern Ireland are:</p>
<ul>
<li>0% up to £125,000</li>
<li>2% from £125,001 to £250,000</li>
<li>5% from £250,001 to £925,000</li>
<li>10% from £925,001 to £1.5 million</li>
<li>12% above £1.5 million</li>
</ul>
<h2>First-time buyer relief</h2>
<p>If you and anyone buying with you have never owned a home anywhere, you pay nothing up to £300,000 and 5% from £300,001 to £500,000. Above £500,000 the relief doesn’t apply at all and you pay the standard rates on the whole price.</p>
<h2>Second homes and buy-to-let</h2>
<p>Buying an additional property adds 5 percentage points to every band, from the first pound, for properties of £40,000 or more. If you’re replacing your main home and sell the old one within three years, you can usually claim that surcharge back. Buyers who aren’t UK resident pay a further 2%.</p>
<h2>Scotland and Wales</h2>
<p>Scotland has Land and Buildings Transaction Tax and Wales has Land Transaction Tax, with different bands, so this calculator doesn’t apply there.</p>
<h2>When it’s due</h2>
<p>Stamp duty must be paid within 14 days of completion. Your solicitor or conveyancer normally files the return and pays it from the money you send them.</p>''',
  faq=[
    ('How much stamp duty do first-time buyers pay?', 'Nothing on the first £300,000 and 5% on the part from £300,001 to £500,000, as long as the price is £500,000 or less. Above that, standard rates apply to the whole price.'),
    ('How much is stamp duty on a £300,000 house?', '£5,000 for a home mover in England or Northern Ireland, nothing for a first-time buyer, and £20,000 for an additional property.'),
    ('Do I pay stamp duty on a second home?', 'Yes. Additional properties of £40,000 or more pay 5 percentage points on top of each band. You can usually reclaim it if you sell your previous main home within three years.'),
  ],
  script='''
import { setup, $, gbp0, plain } from '../guide.js';
import { stampDuty } from '../property.js';

const band = (b) => b.to == null ? `Over ${gbp0.format(b.from)}` : `${gbp0.format(b.from === 0 ? 0 : b.from + 1)} to ${gbp0.format(b.to)}`;
setup({
  fields: {
    price: { min: 1, max: 100000000, money: true },
    buyer: { text: true },
    nonResident: { text: true },
  },
  defaults: { price: 300000, buyer: 'firstTimeBuyer', nonResident: 'no' },
  showInvalid: () => { $('h-total').textContent = '–'; $('bands').innerHTML = ''; },
  render: (d) => {
    const r = stampDuty(d.price, d.buyer, d.nonResident === 'yes');
    $('h-total').textContent = gbp0.format(r.total);
    $('h-sub').textContent = `${plain(+r.effectiveRate.toFixed(2))}% of the price`;
    $('note').innerHTML = r.reliefUnavailable ? '<div class="callout">First-time buyer relief only applies up to £500,000, so standard rates apply to the whole price.</div>'
      : r.reliefApplied ? '<p class="nudge">First-time buyer relief applied.</p>' : '';
    $('bands').innerHTML = '<thead><tr><th>Band</th><th>Rate</th><th>Tax</th></tr></thead><tbody>' +
      r.breakdown.map((b) => `<tr><td>${band(b)}</td><td>${plain(b.rate)}%</td><td>${gbp0.format(b.tax)}</td></tr>`).join('') + '</tbody>';
  },
});
'''))

# ---------- 6. Loan to value ----------
PAGES.append(dict(
  slug='loan-to-value-calculator',
  title='Loan to Value (LTV) Calculator UK: Find Your Mortgage Rate Band | Mortgage Save',
  desc='Work out your mortgage loan-to-value (LTV), which lender band it falls in, and how much you’d need to pay off to reach the next, cheaper band before you remortgage.',
  h1='Loan to value calculator',
  short='Your LTV band and the gap to the next one',
  crumb='Loan to value',
  lede='See your loan-to-value, which rate band it puts you in, and how much less you’d need to owe to reach the next cheaper band.',
  form_title='Your home and mortgage',
  form='\n          '.join([
    pair(field('value', 'Property value', 'money'), field('loan', 'Mortgage balance', 'money')),
  ]),
  results='''<section class="panel">
          <h2>Your loan to value</h2>
          <div class="headline"><span class="k">LTV</span><span class="v" id="h-ltv">–</span><span class="s" id="h-sub"></span></div>
        </section>
        <section class="panel saving">
          <h2>Next band down</h2>
          <div id="out"></div>
        </section>''',
  pitch='Track your balance as it falls and get reminded before your deal ends, so you remortgage at the right time.',
  article='''<h2>What loan to value means</h2>
<p>Loan to value (LTV) is your mortgage balance as a percentage of what your home is worth. A £240,000 mortgage on a £300,000 home is 80% LTV. Lenders price their deals in LTV bands, and the lower your band, the lower the rate they usually offer.</p>
<h2>The usual bands</h2>
<p>Most UK lenders set rates at 60%, 75%, 80%, 85%, 90% and 95% LTV. The biggest rate differences tend to be at the higher end, between 95%, 90% and 85%, but moving from 75% to 60% can still save a meaningful amount over a five-year fix.</p>
<h2>Getting into a lower band</h2>
<ul>
<li><strong>Overpay before you remortgage.</strong> A lump sum or regular overpayments in the months before your deal ends can tip you into the next band. Check your overpayment allowance first, using the <a href="../mortgage-overpayment-allowance-calculator/">allowance calculator</a>.</li>
<li><strong>Get an up-to-date valuation.</strong> If prices near you have risen, your LTV may already be lower than you think. Lenders use their own valuation, so use a realistic figure.</li>
<li><strong>Time it.</strong> Your balance falls every month, so a band you’re just above now may come within reach by the end of your deal.</li>
</ul>''',
  faq=[
    ('How do I calculate my loan to value?', 'Divide your mortgage balance by your property’s value and multiply by 100. A £180,000 balance on a £250,000 home is 72% LTV.'),
    ('What is a good loan to value for a mortgage?', 'The lowest rates are usually at 60% LTV or below. Each band down, such as from 80% to 75%, usually brings a lower rate.'),
    ('Does overpaying reduce my loan to value?', 'Yes. Overpaying reduces your balance, which lowers your LTV and can move you into a cheaper band when you remortgage.'),
  ],
  script='''
import { setup, $, gbp0, plain } from '../guide.js';
import { loanToValue } from '../property.js';

setup({
  fields: {
    value: { min: 1000, max: 100000000, money: true },
    loan: { min: 0, max: 100000000, money: true },
  },
  defaults: { value: 300000, loan: 230000 },
  showInvalid: () => { $('h-ltv').textContent = '–'; $('out').innerHTML = '<p class="empty-over">Check the figures marked in red.</p>'; },
  render: (d) => {
    const r = loanToValue(d.loan, d.value);
    $('h-ltv').textContent = `${plain(+r.percent.toFixed(1))}%`;
    $('h-sub').textContent = r.band == null ? 'Above 95%: most lenders won’t lend at this level' : `In the up to ${r.band}% LTV band`;
    $('out').innerHTML = r.nextLowerBand == null ? '<p class="empty-over">You’re already in the lowest common band (60% or below).</p>' : `
      <div class="saving-grid">
        <div><div class="big">${gbp0.format(r.reductionToNextBand)}</div><div class="k">less to owe to reach ${r.nextLowerBand}% LTV</div></div>
      </div>
      <p>See what paying that off saves with the <a href="../lump-sum-overpayment-calculator/">lump sum calculator</a>.</p>
      <p class="nudge">Get reminded before your deal ends, when you can remortgage into the lower band, with <a href="https://apps.apple.com/app/id6467675017" rel="noopener">Mortgage Save for iPhone</a>.</p>`;
  },
});
'''))

# ---------- 7. Affordability ----------
PAGES.append(dict(
  slug='how-much-can-i-borrow-calculator',
  title='How Much Can I Borrow for a Mortgage? UK Income Multiple Calculator | Mortgage Save',
  desc='Estimate how much UK lenders may let you borrow from your income, at 4, 4.5 and 5.5 times salary, the price that buys with your deposit, and your loan to value.',
  h1='How much can I borrow?',
  short='A quick income-multiple estimate',
  crumb='How much can I borrow',
  lede='A quick estimate of how much lenders may lend on your income, and the price that buys with your deposit.',
  form_title='You and your deposit',
  form='\n          '.join([
    pair(field('income1', 'Your yearly income', 'money'), field('income2', 'Second applicant', 'money', 'Leave 0 if buying alone')),
    pair(field('deposit', 'Deposit', 'money'), field('multiple', 'Income multiple', 'select', None, [('4', '4×'), ('4.5', '4.5× (typical)'), ('5', '5×'), ('5.5', '5.5×')])),
  ]),
  results='''<section class="panel">
          <h2>You could borrow about</h2>
          <div class="headline"><span class="k" id="h-k">At 4.5× income</span><span class="v" id="h-loan">–</span><span class="s" id="h-sub"></span></div>
          <div class="stats">
            <div class="stat"><span class="k">Cautious (4×)</span><span class="v" id="s-low">–</span></div>
            <div class="stat"><span class="k">Higher (5.5×)</span><span class="v" id="s-high">–</span></div>
            <div class="stat"><span class="k">Loan to value</span><span class="v" id="s-ltv">–</span></div>
          </div>
          <p class="fullcalc">See the monthly payment on this loan in the <a href="../" id="full">overpayment calculator</a>.</p>
        </section>''',
  pitch='Once you have a mortgage, keep your figures together and get reminded before your deal ends.',
  article='''<h2>How lenders decide what you can borrow</h2>
<p>Most UK lenders start with an income multiple: typically about 4 to 4.5 times your gross yearly income, or your combined income for a joint mortgage. Some lend up to 5 or 5.5 times for higher earners or certain professions. This calculator shows that range. It’s a starting point, not an offer.</p>
<h2>What else lenders look at</h2>
<ul>
<li><strong>Affordability checks.</strong> Lenders test whether you could still pay if rates rose, using your actual spending, other debts and childcare costs.</li>
<li><strong>Your credit record.</strong> Missed payments or high card balances can lower what you’re offered.</li>
<li><strong>Your deposit.</strong> A bigger deposit means a lower loan to value and usually a better rate, but it doesn’t raise the income multiple.</li>
<li><strong>Income type.</strong> Bonuses, overtime and self-employed income are often only partly counted.</li>
</ul>
<h2>Don’t forget the costs of buying</h2>
<p>Budget for stamp duty, legal fees, a survey and moving costs on top of the deposit. The <a href="../stamp-duty-calculator/">stamp duty calculator</a> works out the tax for England and Northern Ireland.</p>''',
  faq=[
    ('How much can I borrow on a £40,000 salary?', 'At a typical 4.5 times income, about £180,000. Some lenders go to around £160,000 at 4 times or higher for some borrowers, depending on your spending and credit record.'),
    ('Is mortgage borrowing based on gross or net income?', 'Income multiples use gross (before tax) income. Lenders then check affordability against your actual take-home pay and spending.'),
    ('Can I borrow 5 times my salary?', 'Some lenders offer 5 to 5.5 times income, usually for higher earners or certain professions, and often with a bigger deposit.'),
  ],
  script='''
import { setup, $, gbp0, plain, fullCalculatorLink } from '../guide.js';
import { affordability } from '../property.js';

setup({
  fields: {
    income1: { min: 0, max: 10000000, money: true },
    income2: { min: 0, max: 10000000, money: true },
    deposit: { min: 0, max: 100000000, money: true },
    multiple: { text: true },
  },
  defaults: { income1: 40000, income2: 25000, deposit: 30000, multiple: '4.5' },
  check: (d) => (d.income1 + d.income2 > 0 ? {} : { income1: 'Enter an income' }),
  showInvalid: () => { $('h-loan').textContent = '–'; },
  render: (d) => {
    const m = Number(d.multiple);
    const r = affordability([d.income1, d.income2], d.deposit, m);
    $('h-k').textContent = `At ${plain(m)}× income of ${gbp0.format(r.totalIncome)}`;
    $('h-loan').textContent = gbp0.format(r.typicalLoan);
    $('h-sub').textContent = `With your deposit, a home of about ${gbp0.format(r.typicalPrice)}`;
    $('s-low').textContent = gbp0.format(r.lowLoan);
    $('s-high').textContent = gbp0.format(r.highLoan);
    $('s-ltv').textContent = r.typicalLTV == null ? '–' : `${plain(+r.typicalLTV.toFixed(1))}%`;
    if (r.typicalLoan >= 1000) $('full').href = fullCalculatorLink({ loan: Math.round(r.typicalLoan), termYears: 25, dealRate: 4.5, dealYears: 5, svr: 7.25, overpayment: 0 });
  },
});
'''))

# ---------- 8. 2 vs 5 year fix ----------
PAGES.append(dict(
  slug='2-year-vs-5-year-fix-calculator',
  title='2-Year vs 5-Year Fixed Mortgage Calculator: Which Costs Less? | Mortgage Save',
  desc='Compare a 2-year and a 5-year fixed rate mortgage over five years, including fees and the rate you might re-fix at, and find the break-even rate where they cost the same.',
  h1='2-year vs 5-year fix calculator',
  short='Which fix costs less, and the break-even rate',
  crumb='2-year vs 5-year fix',
  lede='Compare a 2-year fix (then a re-fix) with a 5-year fix over the same five years, fees included, and see the re-fix rate where they break even.',
  form_title='The two deals',
  form='\n          '.join([
    pair(field('balance', 'Mortgage balance', 'money'), field('yearsLeft', 'Years left', 'yrs')),
    '<div class="group"><div class="group-title">2-year fix</div>' + pair(field('rate2', 'Rate', 'pct'), field('fees2', 'Fees', 'money')) + '</div>',
    '<div class="group"><div class="group-title">5-year fix</div>' + pair(field('rate5', 'Rate', 'pct'), field('fees5', 'Fees', 'money')) + '</div>',
    '<div class="group"><div class="group-title">After the 2-year fix</div>' + pair(field('refix', 'Rate you re-fix at', 'pct', 'Your best guess for 3 years'), field('refixFees', 'Fees then', 'money')) + '</div>',
  ]),
  results='''<section class="panel saving">
          <h2>Over five years</h2>
          <div id="out"></div>
        </section>
        <section class="panel">
          <h2>Side by side</h2>
          <div class="table-scroll"><table id="cmp"></table></div>
        </section>''',
  pitch='Save both deals as scenarios, compare them side by side and get reminded before your fix ends.',
  article='''<h2>How the comparison works</h2>
<p>A 2-year fix is often cheaper to start with, but after two years you have to re-fix at whatever rates are then on offer, and usually pay fees again. A 5-year fix locks in one rate. This calculator compares both over the same five years on net cost: the interest you pay, plus fees, adjusted for any difference in the balance left at the end.</p>
<h2>The break-even rate</h2>
<p>The break-even rate is the re-fix rate at which both choices cost the same. If you think rates in two years will be below it, the 2-year fix comes out ahead. Above it, the 5-year fix wins. Nobody knows where rates will be, so it helps to ask how far they’d have to move for your choice to go wrong.</p>
<h2>Things the numbers don’t show</h2>
<ul>
<li><strong>Certainty.</strong> A 5-year fix protects your budget for longer.</li>
<li><strong>Flexibility.</strong> Early repayment charges usually apply for the whole fix, so a 5-year deal is costlier to leave if you might move or want to switch.</li>
<li><strong>Loan to value.</strong> After two years your balance is lower and your home may be worth more, which can put you in a cheaper band when you re-fix. See the <a href="../loan-to-value-calculator/">loan to value calculator</a>.</li>
</ul>''',
  faq=[
    ('Is a 2-year or 5-year fixed mortgage better?', 'It depends on what rates do. A 2-year fix wins if you can re-fix below the break-even rate after two years. A 5-year fix wins if rates are higher then, and gives more certainty.'),
    ('Should I include fees when comparing mortgage deals?', 'Yes. A lower rate with a high fee can cost more than a slightly higher rate with no fee, especially on smaller loans. Compare the total cost over the same period.'),
    ('Can I leave a 5-year fix early?', 'Usually only by paying an early repayment charge, often a few percent of the balance, which falls each year of the deal.'),
  ],
  script='''
import { setup, $, gbp0, gbp2, plain } from '../guide.js';
import { compareFixLengths } from '../remortgage.js';

setup({
  fields: {
    balance: { min: 1000, max: 10000000, money: true },
    yearsLeft: { min: 5, max: 50, msg: 'Enter 5 to 50 years' },
    rate2: { min: 0, max: 25 }, fees2: { min: 0, max: 100000, money: true },
    rate5: { min: 0, max: 25 }, fees5: { min: 0, max: 100000, money: true },
    refix: { min: 0, max: 25 }, refixFees: { min: 0, max: 100000, money: true },
  },
  defaults: { balance: 200000, yearsLeft: 25, rate2: 4.1, fees2: 999, rate5: 4.4, fees5: 999, refix: 4.5, refixFees: 999 },
  showInvalid: () => { $('out').innerHTML = '<p class="empty-over">Check the figures marked in red.</p>'; $('cmp').innerHTML = ''; },
  render: (d) => {
    const r = compareFixLengths(d.balance, Math.round(d.yearsLeft * 12), { rate: d.rate2, years: 2, fees: d.fees2 }, { rate: d.rate5, years: 5, fees: d.fees5 }, d.refix, d.refixFees);
    const diff = r.shorterCostsMoreBy;
    const winner = Math.abs(diff) < 1 ? null : diff > 0 ? 'The 5-year fix' : 'The 2-year fix';
    $('out').innerHTML = `
      <div class="saving-grid">
        <div><div class="big">${winner ? gbp0.format(Math.abs(diff)) : 'Same'}</div><div class="k">${winner ? `${winner.toLowerCase().replace('the ', '')} saves` : 'both cost about the same'}</div></div>
        <div><div class="big">${r.breakEvenRefixRate == null ? '–' : plain(r.breakEvenRefixRate) + '%'}</div><div class="k">break-even re-fix rate</div></div>
      </div>
      <p>${r.breakEvenRefixRate == null ? 'At any re-fix rate from 0% to 25%, the same deal comes out ahead.' : `If you can re-fix below ${plain(r.breakEvenRefixRate)}% in two years, the 2-year fix is cheaper. Above it, the 5-year fix is.`}</p>
      <p class="nudge">Don’t miss your re-fix date. <a href="https://apps.apple.com/app/id6467675017" rel="noopener">Mortgage Save for iPhone</a> reminds you before your deal ends.</p>`;
    const row = (k, a, b) => `<tr><td>${k}</td><td>${a}</td><td>${b}</td></tr>`;
    $('cmp').innerHTML = '<thead><tr><th></th><th>2-year</th><th>5-year</th></tr></thead><tbody>' +
      row('Payment, first 2 years', gbp2.format(r.shorter.monthlyPayment), gbp2.format(r.longer.monthlyPayment)) +
      row('Interest over 5 years', gbp0.format(r.shorter.interestPaid), gbp0.format(r.longer.interestPaid)) +
      row('Fees', gbp0.format(r.shorter.upfrontFees), gbp0.format(r.longer.upfrontFees)) +
      row('Balance after 5 years', gbp0.format(r.shorter.endBalance), gbp0.format(r.longer.endBalance)) +
      row('Net cost', gbp0.format(r.shorter.netCost), gbp0.format(r.longer.netCost)) + '</tbody>';
  },
});
'''))

# ---------- 9. Leave a fix early ----------
PAGES.append(dict(
  slug='leave-fixed-rate-early-calculator',
  title='Should I Leave My Fixed Rate Early? Early Repayment Charge Calculator | Mortgage Save',
  desc='Is it worth paying the early repayment charge to leave your fixed rate mortgage for a cheaper deal? Compare staying with leaving over the rest of your current deal.',
  h1='Should I leave my fixed rate early?',
  short='Is a cheaper deal worth the early repayment charge?',
  crumb='Leave a fix early',
  lede='Compare staying on your current fix with paying the early repayment charge to move to a cheaper rate, over the time left on your deal.',
  form_title='Your deal and the new one',
  form='\n          '.join([
    pair(field('balance', 'Mortgage balance', 'money'), field('yearsLeft', 'Years left on mortgage', 'yrs')),
    pair(field('currentRate', 'Current rate', 'pct'), field('monthsLeft', 'Months left on deal', 'num')),
    field('erc', 'Early repayment charge', 'pct', 'Check your mortgage statement or lender’s app'),
    '<div class="group">' + pair(field('newRate', 'New deal rate', 'pct'), field('newFees', 'New deal fees', 'money')) + '</div>',
  ]),
  results='''<section class="panel saving">
          <h2>Over the rest of your deal</h2>
          <div id="out"></div>
        </section>
        <section class="panel">
          <h2>Stay or leave</h2>
          <div class="table-scroll"><table id="cmp"></table></div>
        </section>''',
  pitch='Know exactly when your deal and its charges end, with a reminder before the date.',
  article='''<h2>How the comparison works</h2>
<p>Leaving a fixed deal early usually means an early repayment charge (ERC), a percentage of the balance you repay. The calculator compares the two choices over the months left on your current deal: staying put, or paying the charge plus the new deal’s fees to move to the lower rate now. After your deal ends you’d be free to switch anyway, so that’s the period that matters.</p>
<h2>Where to find your charge</h2>
<p>Your mortgage offer lists the ERC for each year of the deal, often stepping down, for example from 5% in year one to 1% in year five. Your lender’s app or annual statement usually shows the current figure, and many lenders will tell you the exact amount over the phone.</p>
<h2>Cheaper ways to get a lower rate</h2>
<ul>
<li><strong>Lock in a new deal early.</strong> Most lenders let you pick your next deal three to six months before the current one ends, with no charge. See the <a href="../fixed-rate-ending-calculator/">fixed rate ending calculator</a>.</li>
<li><strong>Overpay instead.</strong> Overpaying within your 10% allowance cuts the balance the higher rate applies to, without any charge.</li>
<li><strong>Moving home?</strong> Many fixes are portable, so you may be able to take your rate with you and avoid the charge.</li>
</ul>''',
  faq=[
    ('Is it worth paying an early repayment charge to remortgage?', 'Only if the interest you save on the new rate, over the time left on your current deal, is more than the charge plus the new deal’s fees. With a large charge or little time left, it rarely is.'),
    ('How is an early repayment charge calculated?', 'Usually as a percentage of the balance you repay, set out for each year of the deal in your mortgage offer. It often falls each year.'),
    ('Can I avoid the early repayment charge?', 'You can usually avoid it by waiting until the deal ends, keeping overpayments within the yearly allowance, or porting the deal if you move home.'),
  ],
  script='''
import { setup, $, gbp0, gbp2, plain } from '../guide.js';
import { compareEarlyExit } from '../remortgage.js';

setup({
  fields: {
    balance: { min: 1000, max: 10000000, money: true },
    yearsLeft: { min: 1, max: 50 },
    currentRate: { min: 0, max: 25 },
    monthsLeft: { min: 1, max: 120, msg: 'Enter 1 to 120 months' },
    erc: { min: 0, max: 10 },
    newRate: { min: 0, max: 25 },
    newFees: { min: 0, max: 100000, money: true },
  },
  defaults: { balance: 200000, yearsLeft: 22, currentRate: 5.8, monthsLeft: 30, erc: 3, newRate: 4.2, newFees: 999 },
  check: (d) => (d.monthsLeft > d.yearsLeft * 12 ? { monthsLeft: 'That’s longer than the mortgage' } : {}),
  showInvalid: () => { $('out').innerHTML = '<p class="empty-over">Check the figures marked in red.</p>'; $('cmp').innerHTML = ''; },
  render: (d) => {
    const r = compareEarlyExit(d.balance, Math.round(d.yearsLeft * 12), d.currentRate, Math.round(d.monthsLeft), d.erc, d.newRate, d.newFees);
    const s = r.savingFromLeaving;
    $('out').innerHTML = `
      <div class="saving-grid">
        <div><div class="big">${gbp0.format(Math.abs(s))}</div><div class="k">${s >= 0 ? 'saved by leaving now' : 'more if you leave now'}</div></div>
        <div><div class="big">${gbp0.format(r.earlyRepaymentCharge)}</div><div class="k">early repayment charge</div></div>
      </div>
      <p>${s >= 0 ? `Even after the charge and fees, the ${plain(d.newRate)}% deal costs less over the next ${d.monthsLeft} months.` : `The charge and fees outweigh the lower rate over the ${d.monthsLeft} months left. Waiting until your deal ends is cheaper.`}</p>
      <p class="nudge">Want to switch the moment the charge ends? <a href="https://apps.apple.com/app/id6467675017" rel="noopener">Mortgage Save for iPhone</a> reminds you before your deal ends.</p>`;
    const row = (k, a, b) => `<tr><td>${k}</td><td>${a}</td><td>${b}</td></tr>`;
    $('cmp').innerHTML = '<thead><tr><th></th><th>Stay</th><th>Leave now</th></tr></thead><tbody>' +
      row('Monthly payment', gbp2.format(r.stay.monthlyPayment), gbp2.format(r.leave.monthlyPayment)) +
      row('Interest', gbp0.format(r.stay.interestPaid), gbp0.format(r.leave.interestPaid)) +
      row('Charge and fees', gbp0.format(r.stay.upfrontFees), gbp0.format(r.leave.upfrontFees)) +
      row('Net cost', gbp0.format(r.stay.netCost), gbp0.format(r.leave.netCost)) + '</tbody>';
  },
});
'''))

def home_related():
    items = ''.join(f'\n        <li><a href="{o["slug"]}/">{o["h1"]}<span>{o["short"]}</span></a></li>' for o in PAGES)
    return f'<!-- related:start -->\n    <nav class="related" aria-label="More calculators">\n      <h2>More mortgage calculators</h2>\n      <ul>{items}\n      </ul>\n    </nav>\n    <!-- related:end -->'

def sitemap():
    urls = [BASE + '/'] + [f"{BASE}/{o['slug']}/" for o in PAGES]
    body = ''.join(f'  <url><loc>{u}</loc></url>\n' for u in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}</urlset>\n'

import re
home = open(f'{OUT}/index.html').read()
home = re.sub(r'<!-- related:start -->.*?<!-- related:end -->', lambda m: home_related(), home, flags=re.S)
open(f'{OUT}/index.html', 'w').write(home)
open(f'{OUT}/sitemap.xml', 'w').write(sitemap())

for p in PAGES:
    os.makedirs(f"{OUT}/{p['slug']}", exist_ok=True)
    open(f"{OUT}/{p['slug']}/index.html", 'w').write(page(p))
print([p['slug'] for p in PAGES])
