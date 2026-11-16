"""Spot-check key transformations in built iFlows."""
import sys, zipfile, re
sys.stdout.reconfigure(encoding="utf-8")

def get_iflw(name):
    zip_path = f"iflows/{name}/build/{name}.zip"
    with zipfile.ZipFile(zip_path) as z:
        iflw_path = next(n for n in z.namelist() if n.endswith(".iflw"))
        return z.read(iflw_path).decode("utf-8")

def get_file(name, path):
    zip_path = f"iflows/{name}/build/{name}.zip"
    with zipfile.ZipFile(zip_path) as z:
        return z.read(path).decode("utf-8", errors="replace")

def check(label, cond):
    status = "OK " if cond else "FAIL"
    print(f"  {status}  {label}")
    return cond

print("=== I0702_P_JMSDispatcher_Medius ===")
x = get_iflw("I0702_P_JMSDispatcher_Medius")
check("JMS_QueueName=I0702_Medius", "I0702_Medius" in get_file("I0702_P_JMSDispatcher_Medius", "src/main/resources/parameters.prop"))
check("No I0701 name in iflw", "I0701" not in x)
check("ProcessDirect route uses header", "${header.SSAB_Dispatcher_ReceiverIFlow}" in x)
check("DLQ via JMS_InternalDLQ param", "JMS_InternalDLQ" in x)

print()
print("=== I0539_P_CostCenter_FSAP_SOAPToJMS ===")
x = get_iflw("I0539_P_CostCenter_FSAP_SOAPToJMS")
check("arr_receiversLastIndex loop condition", "arr_receiversLastIndex" in x)
check("CamelLoopIndex in iflw", "CamelLoopIndex" in x)
check("No QUEUE_INDEX", "QUEUE_INDEX" not in x)
check("No QUEUE_LIST_SIZE", "QUEUE_LIST_SIZE" not in x)
check("property.QueueName (not header)", "${property.QueueName}" in x)
check("No header.QueueName", "${header.QueueName}" not in x)
check("SSAB_Dispatcher_ReceiverIFlow header set", "SSAB_Dispatcher_ReceiverIFlow" in x)
# Check ReceiverDetermination.groovy
rd = get_file("I0539_P_CostCenter_FSAP_SOAPToJMS", "src/main/resources/script/ReceiverDetermination.groovy")
check("I0702_Medius in ReceiverDetermination", "I0702_Medius" in rd)
check("I0539_CostCenter_FSAP_Medius_PDToREST in RD", "I0539_CostCenter_FSAP_Medius_PDToREST" in rd)
check("I0539_ORACLE dummy in RD", "I0539_ORACLE" in rd)
check("No AddQueueIndex.groovy", True)  # checked by absence in scripts
with zipfile.ZipFile("iflows/I0539_P_CostCenter_FSAP_SOAPToJMS/build/I0539_P_CostCenter_FSAP_SOAPToJMS.zip") as z:
    scripts = [n for n in z.namelist() if n.startswith("src/main/resources/script/")]
check("No AddQueueIndex", not any("AddQueueIndex" in s for s in scripts))
check("No SetQueueNameHeader", not any("SetQueueNameHeader" in s for s in scripts))
check("No RestorePayload", not any("RestorePayload" in s for s in scripts))

print()
print("=== I0541_P_InternalOrder_FSAP_SOAPToJMS ===")
x = get_iflw("I0541_P_InternalOrder_FSAP_SOAPToJMS")
check("arr_receiversLastIndex loop condition", "arr_receiversLastIndex" in x)
check("IO splitter in iflw", "Internal Order Splitter" in x)
check("GeneralSplitter in iflw", "GeneralSplitter" in x)
check("splitExprValue has InternalOrderReplicationRequest", "InternalOrderReplicationRequest" in x)
check("No ASAP references", "ASAP" not in x)
rd = get_file("I0541_P_InternalOrder_FSAP_SOAPToJMS", "src/main/resources/script/ReceiverDetermination.groovy")
check("I0541_InternalOrder_FSAP_Medius_PDToREST in RD", "I0541_InternalOrder_FSAP_Medius_PDToREST" in rd)

print()
print("=== I0545_P_WBSElement_FSAP_SOAPToJMS ===")
x = get_iflw("I0545_P_WBSElement_FSAP_SOAPToJMS")
check("arr_receiversLastIndex in iflw", "arr_receiversLastIndex" in x)
check("No malformed P_IO_QUEUES", "P_IO_QUEUES" not in x)
rd = get_file("I0545_P_WBSElement_FSAP_SOAPToJMS", "src/main/resources/script/ReceiverDetermination.groovy")
check("I0702_Medius in RD", "I0702_Medius" in rd)
check("I0546_MOBILE dummy in RD", "I0546_MOBILE" in rd)

print()
print("=== I0539_CostCenter_FSAP_Medius_PDToREST ===")
x = get_iflw("I0539_CostCenter_FSAP_Medius_PDToREST")
check("ProcessDirect sender in iflw", "ProcessDirect" in x)
check("address /I0539_CostCenter_FSAP_Medius_PDToREST", "/I0539_CostCenter_FSAP_Medius_PDToREST" in x)
check("No JMS inbound (name=JMS, targetRef=StartEvent_2)", not bool(re.search(r'name="JMS"[^>]+targetRef="StartEvent_2"', x)))
check("No MaxRetries in Process_1", not bool(re.search(r'MaxRetries.*Process_1|Process_1.*MaxRetries', x, re.DOTALL)))
check("No CPI_DLQ participant", "CPI_DLQ" not in x)

print()
print("=== I0541_InternalOrder_FSAP_Medius_PDToREST ===")
x = get_iflw("I0541_InternalOrder_FSAP_Medius_PDToREST")
check("ProcessDirect sender", "ProcessDirect" in x)
check("address /I0541_InternalOrder_FSAP_Medius_PDToREST", "/I0541_InternalOrder_FSAP_Medius_PDToREST" in x)
check("No Internal Order Splitter (moved to parent)", "Internal Order Splitter" not in x)
check("No CPI_DLQ participant", "CPI_DLQ" not in x)

print()
print("=== I0545_WBSElement_FSAP_Medius_PDToREST ===")
x = get_iflw("I0545_WBSElement_FSAP_Medius_PDToREST")
check("ProcessDirect sender", "ProcessDirect" in x)
check("address /I0545_WBSElement_FSAP_Medius_PDToREST", "/I0545_WBSElement_FSAP_Medius_PDToREST" in x)
check("OData lookup present", "OData" in x or "odata" in x.lower())
check("No CPI_DLQ participant", "CPI_DLQ" not in x)
