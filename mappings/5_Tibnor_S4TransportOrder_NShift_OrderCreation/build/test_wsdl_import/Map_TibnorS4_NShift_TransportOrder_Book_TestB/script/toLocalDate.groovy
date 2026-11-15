import com.sap.it.api.mapping.*
import java.time.Instant
import java.time.OffsetDateTime
import java.time.ZoneId
import java.time.format.DateTimeParseException

/*
 * NShift wants the plain local calendar day 'CCYY-MM-DD' for pickup / delivery dates, without a time zone
 * (ConsignmentWS doc 4.1.13 Pickup: a time zone is re-calculated to Stockholm time).
 * S/4 TM sends UTC, e.g. '2026-11-11T22:00:00Z' for midnight 12 Nov in Finland (time zone code 'EET').
 *
 * dateTime : ISO date-time with offset or 'Z' (S/4 GlobalDateTime), or a plain 'yyyy-MM-dd'
 * tzCode   : SAP time zone code of the location (e.g. EET, CET, UTC). Java zone ids and short ids are
 *            accepted; an unknown or empty code falls back to UTC.
 * returns  : 'yyyy-MM-dd' in that time zone, or '' when dateTime is empty
 */
def String toLocalDate(String dateTime, String tzCode) {
    if (dateTime == null || dateTime.trim().isEmpty()) {
        return ""
    }
    String v = dateTime.trim()
    if (v.length() == 10) {
        return v                                    // already a date
    }
    Instant instant
    try {
        instant = OffsetDateTime.parse(v).toInstant()
    } catch (DateTimeParseException e) {
        instant = Instant.parse(v)
    }
    return instant.atZone(zone(tzCode)).toLocalDate().toString()
}

private ZoneId zone(String tzCode) {
    String c = tzCode == null ? "" : tzCode.trim()
    if (c.isEmpty()) {
        return ZoneId.of("UTC")
    }
    try {
        return ZoneId.of(c, ZoneId.SHORT_IDS)
    } catch (Exception e) {
        return ZoneId.of("UTC")
    }
}
