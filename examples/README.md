## Steps taken:
1. VM installed with Windows 7 x64 SP1.
2. User John created.
3. (pre-)Security.evtx acquired.
4. eventlogedit (1 record removed).
5. VM shutdown. 
6. (post-)Security.evtx acquired.


### pre-Security.evtx
  - 123 events.
  - 0 deleted.

### post-Security.evtx
 - 126 events.
 - 1 removed event with eventlogedit.
 - 4 newly added events due to shutdown of system.


## Example with danderspritz-evtx

```bash
$ ./danderspritz_evtx.py -i examples/pre-Security.evtx 

Reading records from examples/pre-Security.evtx...

$ ./danderspritz_evtx.py -i examples/post-Security.evtx -e /dev/stdout

Reading records from examples/post-Security.evtx...
Found a deleted record within record number 104 at offset 0x02A8

<Event xmlns="http://schemas.microsoft.com/win/2004/08/events/event"><System><Provider Name="Microsoft-Windows-Security-Auditing" Guid="{54849625-5478-4994-a5ba-3e3b0328c30d}"></Provider>
<EventID Qualifiers="">4616</EventID>
<Version>1</Version>
<Level>0</Level>
<Task>12288</Task>
<Opcode>0</Opcode>
<Keywords>0x8020000000000000</Keywords>
<TimeCreated SystemTime="2017-12-13 14:56:42.080000"></TimeCreated>
<EventRecordID>105</EventRecordID>
<Correlation ActivityID="" RelatedActivityID=""></Correlation>
<Execution ProcessID="4" ThreadID="56"></Execution>
<Channel>Security</Channel>
<Computer>John-PC</Computer>
<Security UserID=""></Security>
</System>
<EventData><Data Name="SubjectUserSid">S-1-5-18</Data>
<Data Name="SubjectUserName">WIN-F0HKLEEGGT1$</Data>
<Data Name="SubjectDomainName">WORKGROUP</Data>
<Data Name="SubjectLogonId">0x00000000000003e7</Data>
<Data Name="PreviousTime">2017-12-13 14:56:42.205118</Data>
<Data Name="NewTime">2017-12-13 14:56:42.080000</Data>
<Data Name="ProcessId">0x0000000000000334</Data>
<Data Name="ProcessName">C:\Windows\System32\oobe\msoobe.exe</Data>
</EventData>
</Event>
```
