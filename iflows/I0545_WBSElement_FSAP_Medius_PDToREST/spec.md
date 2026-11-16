# I0545_WBSElement_FSAP_Medius_PDToREST

Child iFlow of the FSAP → Medius dispatcher pattern. `I0545_P_WBSElement_FSAP_SOAPToJMS` puts the message on queue `I0710_Medius`. `I0710_P_JMSDispatcher_Medius` calls this flow over ProcessDirect `/I0545_WBSElement_FSAP_Medius_PDToREST`. The flow reads extra WBS data from FSAP over OData ("Query WBS Element"), maps it to Medius JSON (DIMENSION5) and POSTs it to Medius. It also updates User Responsible.

- Source: `_reference/iflows/FSAP_Controlling_MasterData.zip` → `I0545_WBSElement_FSAP_Medius_JMSToREST`
- Build: `py -I tools/iflow_build_fsap_dispatcher.py --only I0545_WBSElement_FSAP_Medius_PDToREST` (`build_i0545_child`, `pd_child_feedback_v110`, `_i0545_extra`)
- Shared helpers: `tools/iflow_lib.py`

## Externalized parameters (v1.1.0)
Same set as I0539 (see `iflows/I0539_CostCenter_FSAP_Medius_PDToREST/spec.md`), plus the FSAP OData receiver:
| Parameter | Used in | Default |
|---|---|---|
| FSAP_Address | OData receiver address | http://fd1.sap.ssab.com |
| FSAP_Authentication / FSAP_Credentials | OData receiver authentication / credential | Basic / FSAP_User_DEV |
| FSAP_CSRFProtected | OData receiver CSRF | true |
| FSAP_Timeout | OData receiver timeout (min) | 1 |
| FSAP_ProxyType | OData receiver proxy type (**new in 1.1.0**) | sapcc |
| OData_metadata_parameters | OData custom query parameters | (empty) |

Content Modifiers: `ErpSourceId` is set in "Set Monitoring Identifiers", and the Medius body step is "Form Payload".

## Decisions
| Date | Question | Answer | Impact |
|---|---|---|---|
| 2026-11-16 | Apply the I0539 v1.1.0 feedback to this flow? | Yes (user: "do the same for the remaining 2 Medius child flows") | Diagram fix, role/CSRF, SE78, shared `HTTP_*` params, Medius_Host, HTTP_MaxBodySize, PD_Address, Medius_ErpSourceId |
| 2026-11-16 | Typo `AlowedCompanies` here too | Fixed (same as I0539) | Renamed to `AllowedCompanies`. A value configured on the tenant must be set again |
| 2026-11-16 | OData proxy type was hard-coded `sapcc` | Externalized as `FSAP_ProxyType` ("the more the better"). The name follows the reference pattern (L1: FSAP_ProxyType on OData V4) | New parameter |

### Not changed (to note)
- `SAP_Sender=FD1-110` here, but `FD1_110` in I0539/I0541. User 2026-11-16: `FD1_110` is right. The user fixes it manually in CPI, so the build keeps the source value. Take it over at the next feedback download.
- The OData receiver's `connectionReuse=true` is not externalized: no reference shows it externalized.
