# I0539_CostCenter_FSAP_Medius_PDToREST

Child iFlow of the FSAP → Medius dispatcher pattern. `I0539_P_CostCenter_FSAP_SOAPToJMS` puts the message on queue `I0710_Medius`. `I0710_P_JMSDispatcher_Medius` calls this flow over ProcessDirect `/I0539_CostCenter_FSAP_Medius_PDToREST`. The flow maps the cost center to Medius JSON and POSTs it to Medius. It also updates User Responsible.

- Source: `_reference/iflows/FSAP_Controlling_MasterData.zip` → `I0540_CostCenter_FSAP_Medius_JMSToREST`
- Build: `py -I tools/iflow_build_fsap_dispatcher.py --only I0539_CostCenter_FSAP_Medius_PDToREST` (`build_i0539_child`, `_i0539_feedback_v110`)
- Shared helpers: `tools/iflow_lib.py` (diagram fix, externalization, checks)

## Externalized parameters (v1.1.0)
| Parameter | Used in | Default |
|---|---|---|
| PD_Address | ProcessDirect sender address | /I0539_CostCenter_FSAP_Medius_PDToREST |
| HTTP_Authorization | Retrigger HTTPS sender, authorization | RoleBased |
| HTTP_UserRole | Retrigger HTTPS sender, user role | SSAB_MessagingSend_InternalOperations |
| HTTP_CSRFProtected | Retrigger HTTPS sender, CSRF | 0 (off) |
| HTTP_MaxBodySize | Retrigger HTTPS sender, max body size (MB) | 40 |
| Medius_Host | both Medius receivers, address host | api.medius.com |
| tenantName | both Medius receivers, address path | ssabQA |
| Medius_Credentials | both Medius receivers, credential | Medius_OAUTH_Test |
| HTTP_Authentication | both Medius receivers, authentication | OAuth2 Client Credentials |
| HTTP_Timeout | both Medius receivers, timeout (ms) | 60000 |
| HTTP_ProxyType | both Medius receivers | default |
| HTTP_ThrowExceptionOnFailure | both Medius receivers | true |
| HTTP_RetryOnConnectionFailure | both Medius receivers | false |
| HTTP_RetryIterations | both Medius receivers | 1 |
| HTTP_RetryInterval | both Medius receivers | 5 |
| HTTP_AllowedRequestHeaders | both Medius receivers | Content-Type |
| HTTP_AllowedResponseHeaders | both Medius receivers | * |
| AllowedCompanies | gateway "Allowed?" (`CH_CompanyCode in '{{AllowedCompanies}}'`) | SE78 |
| Medius_ErpSourceId | property `ErpSourceId` in "Set Monitor Identifiers", used in the Form Payload body | FSAP |
| SAP_Sender / SAP_Receiver / SAP_MessageType | monitoring headers | FD1_110 / Medius / CostCentreReplicationBulkRequest |
| LogPayload / LogPayloadSize | Log Payload | True / 512 |

## Decisions
| Date | Question | Answer | Impact |
|---|---|---|---|
| 2026-11-16 | v1.0.0 test: Main Process in "Integration Process from Source" had no connection (L2, feedback doc screenshot 1) | Cause: the build rewrote Process_1 but not the BPMN diagram. No edges for the new flows, and orphan shapes of the removed DLQ steps were left behind | `iflow_lib.fix_diagram` removes orphans, uses Bhavesh's layout and adds edges. New build check: every flow has an edge and every DI element has a model element |
| 2026-11-16 | Retrigger HTTPS role? (L2) | SSAB: `SSAB_MessagingSend_InternalOperations`. Ask for every other customer | HTTP_UserRole |
| 2026-11-16 | Retrigger CSRF? (L2) | Disabled | HTTP_CSRFProtected=0 |
| 2026-11-16 | Default for allowed companies (L2) | SE78 | AllowedCompanies=SE78 |
| 2026-11-16 | `AlowedCompanies` typo? (L2) | Fix it | Renamed to `AllowedCompanies` in the gateway, prop and propdef. **Configured values on the tenant under the old name are not carried over.** Set SE78 again after import if the tenant had a value |
| 2026-11-16 | Externalize more (L2: "the more the better", names like `HTTP_Timeout`, `HTTP_ThrowExceptionOnFailure`) | One shared `HTTP_*` set for both Medius receivers (`HTTP`, `HTTP_UserResponsible`) | See the table above |
| 2026-11-16 | Extras (Medius host, body size, ErpSourceId, PD address)? | No preference, so all of them were included | `Medius_Host`, `HTTP_MaxBodySize`, `Medius_ErpSourceId`, `PD_Address`. `PD_Address` must stay equal to the parent's receiver iFlow name |
| 2026-11-16 | Unused `ssabQA` parameter | Remove | Removed. `QUEUE_NAME` and `MaxRetries` also removed from propdef (CPI had already dropped them) |
| 2026-11-16 | spec.md per iFlow folder? | Yes | This file |

### UNVERIFIED (L4), to check on import
- **propdef `param_references` for the new HTTP receiver parameters.** These follow the reference pattern (`attribute_category` = system name, `attrId::<key>`). The references only show `httpAddressWithoutQuery` and `credentialName` for the HTTP receiver. CPI rewrites propdef on save. The `HTTP_Authentication` reference uses category `Medius.Receiver.Auth`, like `credentialName`.
- **`{{HTTP_Authentication}}`, `{{HTTP_ProxyType}}`, `{{HTTP_ThrowExceptionOnFailure}}`, `{{HTTP_RetryOnConnectionFailure}}`:** these are combobox and checkbox fields. Their values are typed as `xsd:string`, with the same text as the hard-coded values. Check that Configure shows them correctly.
- **ErpSourceId:** it is not externalized inside the Content Modifier body, because no reference shows `{{…}}` in a body. Instead it is a constant `{{…}}` property row in "Set Monitor Identifiers", the same pattern as `LogPayloadSize`, and the body reads `${property.ErpSourceId}`.
