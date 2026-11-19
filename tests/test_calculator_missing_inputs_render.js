// Exercise the actual inline calculator script with blank, zero and invalid inputs.
const fs = require('fs');
const vm = require('vm');
const page = fs.readFileSync('site/calculator.html', 'utf8');
const script = page.match(/<script>\s*([\s\S]*?)<\/script>/)[1];
const fields = { entries:'7', buyIn:'371.43', nights:'7', rate:'119', resortFee:'55', taxRate:'13.38', parking:'20' };
const form = {addEventListener: (event, fn) => { form.update = fn; }};
for (const [name, value] of Object.entries(fields)) form[name] = {value, validity:{valid:true}};
const output = {innerHTML:'', textContent:''}, breakdown = {innerHTML:'', textContent:''};
const document = {
  getElementById: id => ({tripForm:form, result:output, breakdown})[id],
  querySelector: () => null,
  querySelectorAll: () => []
};
vm.runInNewContext(script, {document, fetch: () => new Promise(() => {}), Number, isFinite});
function assert(condition, message) { if (!condition) throw new Error(message); }
for (const name of ['entries', 'buyIn', 'nights', 'rate', 'resortFee', 'taxRate']) {
  form[name].value = ''; form.update();
  assert(output.textContent === 'Core trip estimate unavailable', `blank ${name} must prevent a core estimate`);
  form[name].value = fields[name];
}
form.parking.value = ''; form.update();
assert(output.innerHTML.includes('Core trip estimate:') && output.innerHTML.includes('parking-inclusive total unavailable'), 'missing parking must not be treated as free');
form.parking.value = '0'; form.update();
assert(output.innerHTML.includes('including parking'), 'explicit zero must be allowed');
form.taxRate.validity.valid = false; form.update();
assert(output.textContent === 'Core trip estimate unavailable', 'invalid core input must not be used');
assert(!page.includes('data-preset="quote"'), 'a one-night rate is not a seven-night quote');
console.log('calculator missing-input rendering passed');
