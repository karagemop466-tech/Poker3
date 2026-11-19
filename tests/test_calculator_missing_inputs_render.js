// Exercise the actual inline calculator script with blanks, explicit zero,
// invalid values, and a hotel preset whose price/tax/parking are unpublished.
const fs = require('fs');
const vm = require('vm');
const page = fs.readFileSync('site/calculator.html', 'utf8');
const script = page.match(/<script>\s*([\s\S]*?)<\/script>/)[1];
const initial = {
  entries: '7', buyIn: '371.43', nights: '7', rate: '119',
  resortFee: '55', taxRate: '13.38', parking: '20'
};
const form = { addEventListener: (event, fn) => { form.update = fn; } };
for (const [name, value] of Object.entries(initial)) {
  form[name] = { value, validity: { valid: true } };
}
const output = { innerHTML: '', textContent: '' };
const breakdown = { innerHTML: '', textContent: '' };
const compareBody = { innerHTML: '' };
const compareNote = { textContent: '' };
const quote = { textContent: '', append() {} };
const presetButton = {
  dataset: { rate: '', fee: '55', tax: '', parking: '' },
  addEventListener(event, fn) { this.onClick = fn; }
};
const presetHost = {
  innerHTML: '',
  querySelectorAll: () => [presetButton]
};
const db = {
  hotels: [{
    id: 'unpriced', name: 'Unpriced property', baseRateFloor: null,
    derivedNightlyLow: null, resortFee: 55, taxRate: null, parkingPerNight: null
  }],
  tripCostModel: {
    entries: 7, buyIn: 371.43, tournamentTotal: 2600,
    nights: 7, liveQuote: null
  }
};
const document = {
  getElementById: id => ({ tripForm: form, result: output, breakdown })[id],
  querySelector: selector => ({
    '[data-hotel-presets]': presetHost,
    '[data-cost-compare]': compareBody,
    '[data-compare-note]': compareNote,
    '[data-dated-quote]': quote
  })[selector] || null,
  querySelectorAll: () => [],
  createElement: () => ({})
};

vm.runInNewContext(script, {
  document,
  fetch: () => Promise.resolve({ json: async () => db }),
  Number,
  setImmediate,
  console
});

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

setImmediate(() => {
  for (const name of ['entries', 'buyIn', 'nights', 'rate', 'resortFee', 'taxRate']) {
    form[name].value = '';
    form.update();
    assert(/unavailable/i.test(output.textContent + ' ' + output.innerHTML), `blank ${name} must prevent a core estimate`);
    form[name].value = initial[name];
  }

  form.parking.value = '';
  form.update();
  assert(output.innerHTML.includes('Core trip estimate:'), 'missing parking must keep a known core estimate');
  assert(output.innerHTML.includes('parking-inclusive total unavailable'), 'missing parking must not be treated as free');

  form.parking.value = '0';
  form.update();
  assert(output.innerHTML.includes('including parking'), 'explicit zero parking must be allowed');

  form.taxRate.validity.valid = false;
  form.update();
  assert(/unavailable/i.test(output.textContent + ' ' + output.innerHTML), 'invalid core input must not be used');
  form.taxRate.validity.valid = true;

  assert(presetButton.onClick, 'hotel preset click handler was not installed');
  assert(presetHost.innerHTML.includes('data-rate=""'), 'unpublished room rate must stay blank in the preset');
  assert(presetHost.innerHTML.includes('data-tax=""'), 'unpublished tax must stay blank in the preset');
  assert(presetHost.innerHTML.includes('data-parking=""'), 'unpublished parking must stay blank in the preset');
  presetButton.onClick();
  assert(form.rate.value === '' && form.taxRate.value === '' && form.parking.value === '',
    'selecting a hotel with missing values must clear stale values rather than reusing or zeroing them');
  assert(/unavailable/i.test(output.textContent + ' ' + output.innerHTML), 'an unpriced hotel must not produce an estimate');
  assert(!page.includes('data-preset="quote"'), 'a different-date checkout average must not be a rate preset');
  console.log('calculator missing-input rendering passed');
});
