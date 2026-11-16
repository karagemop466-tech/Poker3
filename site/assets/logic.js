(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.PokerPlannerLogic = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const NO_EXTRA_STATUSES = new Set(["not-allowed", "not-available", "none", "no"]);

  function strictEligible(event) {
    const rules = event && event.rules ? event.rules : {};
    if ((event && event.strictStatus) !== "verified") return false;
    if (!rules.singleEntry || rules.singleEntry.status !== "confirmed") return false;
    return ["reEntry", "rebuy", "addOn", "paidChipAdvantage"].every((key) => {
      return rules[key] && NO_EXTRA_STATUSES.has(rules[key].status);
    });
  }

  function parseTime(value) {
    const match = String(value || "").trim().match(/^(\d{1,2})(?::(\d{2}))?\s*(AM|PM)$/i);
    if (!match) return null;
    let hours = Number(match[1]);
    const minutes = Number(match[2] || 0);
    const period = match[3].toUpperCase();
    if (hours < 1 || hours > 12 || minutes > 59) return null;
    hours = (hours % 12) + (period === "PM" ? 12 : 0);
    return hours * 60 + minutes;
  }

  function scheduleConflicts(events, bufferMinutes) {
    const buffer = Math.max(0, Number(bufferMinutes) || 0);
    const grouped = new Map();
    for (const event of events || []) {
      if (!event.dateISO) continue;
      const minute = parseTime(event.time);
      if (minute === null) continue;
      if (!grouped.has(event.dateISO)) grouped.set(event.dateISO, []);
      grouped.get(event.dateISO).push({ event, minute });
    }
    const conflicts = [];
    for (const [date, rows] of grouped.entries()) {
      rows.sort((a, b) => a.minute - b.minute || String(a.event.id).localeCompare(String(b.event.id)));
      for (let i = 0; i < rows.length; i += 1) {
        for (let j = i + 1; j < rows.length; j += 1) {
          const gap = rows[j].minute - rows[i].minute;
          if (gap > buffer) break;
          if (rows[i].event.id === rows[j].event.id) continue;
          conflicts.push({
            date,
            first: rows[i].event,
            second: rows[j].event,
            gapMinutes: gap,
            sameVenue: rows[i].event.venueId === rows[j].event.venueId,
          });
        }
      }
    }
    return conflicts.sort((a, b) => a.date.localeCompare(b.date) || a.gapMinutes - b.gapMinutes);
  }

  function wholeNights(arrival, departure) {
    if (!arrival || !departure) return null;
    const start = Date.parse(`${arrival}T00:00:00Z`);
    const end = Date.parse(`${departure}T00:00:00Z`);
    if (!Number.isFinite(start) || !Number.isFinite(end) || end <= start) return null;
    return Math.round((end - start) / 86400000);
  }

  function calculateStay(input) {
    const errors = [];
    const nights = wholeNights(input.arrival, input.departure);
    if (!nights) errors.push("Enter a valid arrival and later departure date.");
    const rooms = Math.max(1, Math.floor(Number(input.rooms) || 1));
    const occupants = Math.max(0, Number(input.adults) + Number(input.children));
    const vehicles = Math.max(0, Math.floor(Number(input.vehicles) || 0));
    const includedVehicles = Math.max(0, Math.floor(Number(input.parkingIncludedVehicles) || 0));
    const paidVehicles = Math.max(0, vehicles - includedVehicles);
    const roomRate = input.roomRate === "" || input.roomRate == null ? null : Number(input.roomRate);
    const resortFee = input.resortFee === "" || input.resortFee == null ? null : Number(input.resortFee);
    const roomTax = input.roomTaxPercent === "" || input.roomTaxPercent == null ? null : Number(input.roomTaxPercent);
    const feeTax = input.resortFeeTaxPercent === "" || input.resortFeeTaxPercent == null ? null : Number(input.resortFeeTaxPercent);
    const extraRate = input.extraOccupantRate === "" || input.extraOccupantRate == null ? null : Number(input.extraOccupantRate);
    const parkingRate = input.parkingPerVehicleNight === "" || input.parkingPerVehicleNight == null ? null : Number(input.parkingPerVehicleNight);
    const otherFees = input.otherMandatoryFees === "" || input.otherMandatoryFees == null ? null : Number(input.otherMandatoryFees);

    if (roomRate === null || !Number.isFinite(roomRate) || roomRate < 0) errors.push("Enter the exact room rate per room, per night.");
    if (resortFee === null || !Number.isFinite(resortFee) || resortFee < 0) errors.push("Confirm and enter the resort fee (enter 0 only if the booked offer has none).");
    if (roomTax === null || !Number.isFinite(roomTax) || roomTax < 0) errors.push("Enter the applicable room / occupancy tax rate.");
    if (resortFee !== null && resortFee > 0 && (feeTax === null || !Number.isFinite(feeTax) || feeTax < 0)) errors.push("Enter the tax rate applied to the resort fee.");
    if (nights && occupants > rooms * 2 && (extraRate === null || !Number.isFinite(extraRate) || extraRate < 0)) errors.push("Confirm the fee for occupants above two per room.");
    if (paidVehicles > 0 && (parkingRate === null || !Number.isFinite(parkingRate) || parkingRate < 0)) errors.push("Enter the overnight parking cost for vehicles not included with the stay.");
    if (otherFees === null || !Number.isFinite(otherFees) || otherFees < 0) errors.push("Enter other mandatory fees for the stay (use 0 if none). ");

    const safe = (value) => value === null || !Number.isFinite(value) ? 0 : value;
    const roomSubtotal = nights ? safe(roomRate) * nights * rooms : 0;
    const resortFeeTotal = nights ? safe(resortFee) * nights * rooms : 0;
    const extraOccupants = Math.max(0, occupants - rooms * 2);
    const extraOccupantTotal = nights ? extraOccupants * safe(extraRate) * nights : 0;
    const parkingTotal = nights ? paidVehicles * safe(parkingRate) * nights : 0;
    const roomTaxTotal = (roomSubtotal + extraOccupantTotal) * safe(roomTax) / 100;
    const resortFeeTaxTotal = resortFeeTotal * safe(feeTax) / 100;
    const knownPreTax = roomSubtotal + resortFeeTotal + extraOccupantTotal + parkingTotal + safe(otherFees);
    const complete = errors.length === 0;
    const total = complete ? knownPreTax + roomTaxTotal + resortFeeTaxTotal : null;
    const round = (number) => Math.round((number + Number.EPSILON) * 100) / 100;
    return {
      complete,
      errors,
      nights,
      rooms,
      occupants,
      roomSubtotal: round(roomSubtotal),
      resortFeeTotal: round(resortFeeTotal),
      extraOccupantTotal: round(extraOccupantTotal),
      parkingTotal: round(parkingTotal),
      otherFees: round(safe(otherFees)),
      roomTaxTotal: round(roomTaxTotal),
      resortFeeTaxTotal: round(resortFeeTaxTotal),
      knownPreTax: round(knownPreTax),
      total: total === null ? null : round(total),
      nightlyAverage: total === null || !nights ? null : round(total / nights),
    };
  }

  function filterEvents(events, options) {
    const opts = options || {};
    const query = String(opts.query || "").trim().toLowerCase();
    return (events || []).filter((event) => {
      if (opts.strictOnly && !strictEligible(event)) return false;
      if (opts.venue && event.venueId !== opts.venue) return false;
      if (opts.from && (!event.dateISO || event.dateISO < opts.from)) return false;
      if (opts.to && (!event.dateISO || event.dateISO > opts.to)) return false;
      if (opts.datedOnly && !event.dateISO) return false;
      if (query && ![
        event.date, event.time, event.venue, event.event, event.buyIn, event.guarantee,
        event.format, event.entryStatus, event.eventNumber, ...(event.tags || []),
      ].join(" ").toLowerCase().includes(query)) return false;
      return true;
    });
  }

  return { strictEligible, parseTime, scheduleConflicts, wholeNights, calculateStay, filterEvents };
});
