### Table of Contents

 * 1 Emails are matched without regard to case (REV-001)
 * 2 Hashes of old emails link records too (REV-002)
 * 3 An incomplete case verifies every relevant record (REV-003)
 * 4 The owning service is reported, not the copy's location (REV-004)
 * 5 A complete listing without the record proves its absence (REV-005)
 * 6 A request row that cannot be read still gets its output row (REV-006)

# 1 Emails are matched without regard to case _(REV-001)_ {#REV-001}

Email addresses shall be compared without regard to upper and lower case, both when the request email is matched to an identity and when evidence is matched to the subject.

*Parent links: CHR-309*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | functional |
| modality | shall |
| verification | test |
| rationale | Revealed in step 3 (data analysis), not stated by any input line. Evidence lists some emails in upper case, for example CHOI.JIHOON94@GMAIL.COM in evidence_03 (customer_account_handover_20261001.txt). Rechecked in step 4: 20 of the 518 evaluation requests write the request email with upper-case letters.
 |


# 2 Hashes of old emails link records too _(REV-002)_ {#REV-002}

A record shall be linked to the subject also through the email hash of any current or old email address of the subject; the email hash is the SHA-256 of the lower-case email address.

*Parent links: CHR-304, CHR-309*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | functional |
| modality | shall |
| verification | test |
| rationale | Revealed in step 3 (data analysis), not stated by any input line. Sample case_12: analytics_9914 is linked to the subject only through the hash of an old email (correlation_key in evidence_01). The hash rule was recomputed and matches user_identities.csv.
 |


# 3 An incomplete case verifies every relevant record _(REV-003)_ {#REV-003}

In an INCOMPLETE case, the verification phase shall contain one check for every relevant record, data flow, and backup: also for those that already comply and for those that are retained.

*Parent links: CHR-434*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | functional |
| modality | shall |
| verification | test |
| rationale | Revealed in step 3 (data analysis), not stated by any input line. All 22 INCOMPLETE sample answers do this, for example case_06 verifies account_006 (already absent) next to search_001 (remediated).
 |


# 4 The owning service is reported, not the copy's location _(REV-004)_ {#REV-004}

Each step shall name the service that owns the resource (account -> account_service, search -> search_service, analytics -> analytics_platform, support -> support_platform, export -> export_service, data_flow -> integration_service, backup -> backup_service, audit_record -> security_service, tombstone -> identity_service), also when the copy was found in a replica or another store.

*Parent links: CHR-309, CHR-439*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | shall |
| verification | test |
| rationale | Revealed in step 3 (data analysis), not stated by any input line. All steps of the 32 sample answers follow this mapping. Sample case_05 reports account_005 under account_service although the copy is in a failover replica table.
 |


# 5 A complete listing without the record proves its absence _(REV-005)_ {#REV-005}

When an evidence item lists all records of a store (a snapshot table or collection) at a time at or before audit_at, a record of that store's kind that is not in the listing shall count as absent from that store, and that evidence item proves the absence.

*Parent links: CHR-313, CHR-436*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | functional |
| modality | shall |
| verification | test |
| rationale | Revealed in step 4, when the interfaces were rechecked against the 32 sample answers: 4 cited verification steps prove ABSENT with evidence that never names the record (case_01, case_02, case_04: evidence_54, an SQL snapshot of the customer_profiles tables; case_31: evidence_51, a JSON snapshot bundle). Found with a script that checks whether each cited evidence file contains the step's resource_id.
 |


# 6 A request row that cannot be read still gets its output row _(REV-006)_ {#REV-006}

When a row of deletion_requests.csv fails the input checks, the row shall be skipped and reported, but its case_id, when readable, shall still be passed on, so that the case gets its output row.

*Parent links: CHR-403, CHR-503, EXT-501*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | functional |
| modality | shall |
| verification | test |
| rationale | Revealed in step 5, while designing the input reader's checks: skipping a bad row, as for the other files, would silently drop its case from output.csv, and a submission without that row breaks CHR-403. The real dataset has no such row; the protection is for unexpected or misleading input (EXT-501).
 |


