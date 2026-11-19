// Execute the hotel-page cost widget's actual update function with stub inputs.
const fs = require('fs');
const vm = require('vm');
const source = fs.readFileSync('site/assets/app.js', 'utf8');
const marker = "const calc = document.querySelector('[data-calculator]');";
const markerAt = source.indexOf(marker);
const start = source.indexOf('const update = () => {', markerAt);
const end = source.indexOf('\n    calc.querySelectorAll', start);
if (markerAt < 0 || start < 0 || end < 0) throw new Error('hotel cost update function was not found');
const updateSource = source.slice(start, end) + '\nupdate();';

function render(values, invalid = []) {
  const inputs = Object.fromEntries(Object.entries(values).map(([id, value]) => [id, {
    value: String(value), validity: { valid: !invalid.includes(id) }
  }]));
  const output = { innerHTML: '', textContent: '' };
  vm.runInNewContext(updateSource, {
    Number,
    document: { getElementById: id => id === 'calc-out' ? output : inputs[id] }
  });
  return output;
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

const defaults = { 'calc-rate': 119, 'calc-fee': 55, 'calc-tax': 13.38, 'calc-nights': 7 };
let output = render(defaults);
assert(output.innerHTML.includes('$197.28</strong> per night'), 'published components should calculate a true nightly cost');
assert(output.innerHTML.includes('$1380.96</strong> for 7 nights'), 'valid nights should produce the stay total');

for (const name of ['calc-rate', 'calc-fee', 'calc-tax']) {
  const values = { ...defaults, [name]: '' };
  output = render(values);
  assert(output.textContent.includes('unavailable'), `blank ${name} must not produce a zero-cost result`);
}
output = render(defaults, ['calc-tax']);
assert(output.textContent.includes('unavailable'), 'invalid tax must not produce a result');

output = render({ ...defaults, 'calc-nights': '' });
assert(output.innerHTML.includes('$197.28</strong> per night'), 'a missing night count should keep the known nightly cost');
assert(output.innerHTML.includes('stay total unavailable'), 'a missing night count must not be treated as zero');

output = render({ 'calc-rate': 0, 'calc-fee': 0, 'calc-tax': 0, 'calc-nights': 0 });
assert(output.innerHTML.includes('$0.00</strong> per night'), 'explicit zero values must remain valid');
assert(output.innerHTML.includes('$0.00</strong> for 0 nights'), 'explicit zero nights must remain valid');

output = render({ ...defaults, 'calc-nights': 1.5 }, ['calc-nights']);
assert(output.innerHTML.includes('stay total unavailable'), 'invalid fractional nights must not be truncated');
console.log('hotel cost widget missing-input rendering passed');
