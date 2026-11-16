#!/usr/bin/env node
const assert = require('node:assert/strict');
const logic = require('../site/assets/logic.js');

const verified = {
  strictStatus: 'verified',
  rules: {
    singleEntry: { status: 'confirmed' },
    reEntry: { status: 'not-allowed' },
    rebuy: { status: 'not-allowed' },
    addOn: { status: 'not-allowed' },
    paidChipAdvantage: { status: 'not-available' },
  },
};
assert.equal(logic.strictEligible(verified), true);
assert.equal(logic.strictEligible({ ...verified, rules: { ...verified.rules, addOn: { status: 'not-stated' } } }), false);
assert.equal(logic.strictEligible({ ...verified, strictStatus: 'unverified' }), false);

assert.equal(logic.parseTime('9:10 AM'), 550);
assert.equal(logic.parseTime('12:00 PM'), 720);
assert.equal(logic.parseTime('12:00 AM'), 0);
assert.equal(logic.parseTime('not a time'), null);

const events = [
  { id: 'a', dateISO: '2026-11-27', time: '11:00 AM', venueId: 'wynn' },
  { id: 'b', dateISO: '2026-11-27', time: '11:10 AM', venueId: 'venetian' },
  { id: 'c', dateISO: '2026-11-27', time: '1:00 PM', venueId: 'wynn' },
  { id: 'undated', dateISO: '', time: '8:00 AM', venueId: 'aria' },
];
const conflicts = logic.scheduleConflicts(events, 30);
assert.equal(conflicts.length, 1);
assert.equal(conflicts[0].gapMinutes, 10);
assert.equal(conflicts[0].sameVenue, false);

const cost = logic.calculateStay({
  arrival: '2026-12-10', departure: '2026-12-14', rooms: 1, adults: 2, children: 0, vehicles: 1,
  roomRate: 100, roomTaxPercent: 13.38, resortFee: 55, resortFeeTaxPercent: 13.38,
  extraOccupantRate: '', parkingPerVehicleNight: 20, otherMandatoryFees: 0,
});
assert.equal(cost.complete, true);
assert.equal(cost.nights, 4);
assert.equal(cost.roomSubtotal, 400);
assert.equal(cost.resortFeeTotal, 220);
assert.equal(cost.total, 782.96);

const incomplete = logic.calculateStay({
  arrival: '2026-12-10', departure: '2026-12-14', rooms: 1, adults: 2, children: 0, vehicles: 0,
  roomRate: 100, roomTaxPercent: '', resortFee: 55, resortFeeTaxPercent: '',
  extraOccupantRate: '', parkingPerVehicleNight: 0, otherMandatoryFees: 0,
});
assert.equal(incomplete.complete, false);
assert.equal(incomplete.total, null);
assert.ok(incomplete.errors.some((error) => error.includes('tax rate')));

const filtered = logic.filterEvents(events, { from: '2026-11-27', to: '2026-11-27', datedOnly: true, venue: 'wynn' });
assert.equal(filtered.length, 2);

const snapshot = require('../site/data.json');
assert.equal(snapshot.scheduleCoverage.listedRows, 83);
assert.equal(snapshot.scheduleCoverage.lastDate, '2026-12-23');
assert.equal(logic.filterEvents(snapshot.tournaments, { strictOnly: true }).length, 0);
const realConflicts = logic.scheduleConflicts(snapshot.tournaments.filter((event) => event.dateISO), 30);
assert.ok(realConflicts.some((item) => item.date === '2026-11-27' && item.gapMinutes === 10 && !item.sameVenue));

console.log('OK · strict-entry gate · date/time parser · schedule-gap detector · hotel estimate · date filters · real snapshot');
