# -*- coding: utf-8 -*-
"""Arc 4's five generated request families, 0.12.12-dev.

Taken from `CAMPAIGN_CHART.md` arc 4 verbatim -- "Clients request surveys, samples, instruments,
rescue, secure access" -- one family per named item, nothing invented.

Every route is satisfiable by one of the seven checks that exist, against a def that exists:
  * things:   Steel, GlowPod, ComponentIndustrial (all catalogue-carried, so Purchase can refuse
              before contact and Deliver can refuse for a thing the branch cannot get)
  * logs:     route, entity
  * projects: RR_Measurement_SecondReading, RR_Fieldcraft_RescueTraining, RR_GateStandingConnection

No prerequisiteRequests: a generated family is gated by the eligibility filter, not by a chain.
No expiry: there is no field for one.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MOD = os.path.join(REPO, 'Mod', 'Rimrooms - Async Industries', '1.6')
DEFS = os.path.join(MOD, 'Defs', 'RimroomsRequestDefs', 'RR_Requests.xml')
KEYED = os.path.join(MOD, 'Languages', 'English', 'Keyed', 'RR_Requests.xml')

DEF_BLOCK = u"""
  <!-- ===================================================================================
       ARC 4, GENERATED. "Clients request surveys, samples, instruments, rescue, secure access"
       one family per named item.

       These are not tutorial requests. They carry no tutorialOrder and no prerequisites: the
       eligibility filter decides whether the branch can take two routes of two different kinds
       from the pool below, and only then is the family offered. A family may be asked for more
       than once, and progress on a generated request is counted from the moment it appeared.
       =================================================================================== -->

  <!-- surveys -->
  <RimroomsAsyncIndustries.Company.RimroomsRequestDef>
    <defName>RR_Request_ClientSurvey</defName>
    <label>a client wants a coordinate written up</label>
    <description>Somebody is paying for paperwork about a place they will never go. They want the layout, the way through it and what it does to a compass, in a form their own people can read.\\n\\nThe company does not ask how you know. A filed record will do, and so will somebody who was there.</description>
    <arc>4</arc>
    <paymentUsd>6000000</paymentUsd>
    <successRoutes>
      <li>
        <kind>Document</kind>
        <labelKey>RR_Route_ClientSurveyFileLabel</labelKey>
        <descriptionKey>RR_Route_ClientSurveyFileDesc</descriptionKey>
        <logKind>route</logKind>
      </li>
      <li>
        <kind>Testify</kind>
        <labelKey>RR_Route_ClientSurveySpeakLabel</labelKey>
        <descriptionKey>RR_Route_ClientSurveySpeakDesc</descriptionKey>
        <logKind>route</logKind>
      </li>
    </successRoutes>
  </RimroomsAsyncIndustries.Company.RimroomsRequestDef>

  <!-- samples -->
  <RimroomsAsyncIndustries.Company.RimroomsRequestDef>
    <defName>RR_Request_ClientSamples</defName>
    <label>a client wants material by the crate</label>
    <description>A buyer wants bulk metal and has been told it came out of somewhere unusual. They are not going to check.\\n\\nRecover it, or make the number up out of stock and keep the difference. The company genuinely does not mind which.</description>
    <arc>4</arc>
    <paymentUsd>9000000</paymentUsd>
    <successRoutes>
      <li>
        <kind>Deliver</kind>
        <labelKey>RR_Route_ClientSamplesRecoverLabel</labelKey>
        <descriptionKey>RR_Route_ClientSamplesRecoverDesc</descriptionKey>
        <thingDefName>Steel</thingDefName>
        <count>250</count>
      </li>
      <li>
        <kind>Purchase</kind>
        <labelKey>RR_Route_ClientSamplesBuyLabel</labelKey>
        <descriptionKey>RR_Route_ClientSamplesBuyDesc</descriptionKey>
        <thingDefName>Steel</thingDefName>
        <count>250</count>
      </li>
    </successRoutes>
  </RimroomsAsyncIndustries.Company.RimroomsRequestDef>

  <!-- instruments -->
  <RimroomsAsyncIndustries.Company.RimroomsRequestDef>
    <defName>RR_Request_ClientInstruments</defName>
    <label>a client wants instruments left running</label>
    <description>A research outfit wants readings taken somewhere nobody sensible would stand for long. They have sent no equipment and no people.\\n\\nPut markers down and let them run, or show the company a method it can sell as one.</description>
    <arc>4</arc>
    <paymentUsd>11000000</paymentUsd>
    <successRoutes>
      <li>
        <kind>Deliver</kind>
        <labelKey>RR_Route_ClientInstrumentsPlaceLabel</labelKey>
        <descriptionKey>RR_Route_ClientInstrumentsPlaceDesc</descriptionKey>
        <thingDefName>GlowPod</thingDefName>
        <count>6</count>
      </li>
      <li>
        <kind>Research</kind>
        <labelKey>RR_Route_ClientInstrumentsMethodLabel</labelKey>
        <descriptionKey>RR_Route_ClientInstrumentsMethodDesc</descriptionKey>
        <projectDefName>RR_Measurement_SecondReading</projectDefName>
      </li>
    </successRoutes>
  </RimroomsAsyncIndustries.Company.RimroomsRequestDef>

  <!-- rescue -->
  <RimroomsAsyncIndustries.Company.RimroomsRequestDef>
    <defName>RR_Request_ClientRescue</defName>
    <label>a client has lost somebody down there</label>
    <description>Another operation sent people through a door they did not understand and the people did not come back. Their employer is paying this branch because it has stopped believing its own staff.\\n\\nThe company will take a trained capability or a first-hand account. It would prefer the capability, because it can sell that again.</description>
    <arc>4</arc>
    <paymentUsd>15000000</paymentUsd>
    <successRoutes>
      <li>
        <kind>Research</kind>
        <labelKey>RR_Route_ClientRescueTrainingLabel</labelKey>
        <descriptionKey>RR_Route_ClientRescueTrainingDesc</descriptionKey>
        <projectDefName>RR_Fieldcraft_RescueTraining</projectDefName>
      </li>
      <li>
        <kind>Testify</kind>
        <labelKey>RR_Route_ClientRescueAccountLabel</labelKey>
        <descriptionKey>RR_Route_ClientRescueAccountDesc</descriptionKey>
        <logKind>entity</logKind>
      </li>
    </successRoutes>
  </RimroomsAsyncIndustries.Company.RimroomsRequestDef>

  <!-- secure access -->
  <RimroomsAsyncIndustries.Company.RimroomsRequestDef>
    <defName>RR_Request_ClientSecureAccess</defName>
    <label>a client wants a door they can rely on</label>
    <description>A paying customer wants to be able to go in and come out on a schedule of their own choosing, and has made it clear they consider that an ordinary thing to ask for.\\n\\nMake the connection hold, or hand over enough parts that somebody else can.</description>
    <arc>4</arc>
    <paymentUsd>18000000</paymentUsd>
    <successRoutes>
      <li>
        <kind>Research</kind>
        <labelKey>RR_Route_ClientAccessStandingLabel</labelKey>
        <descriptionKey>RR_Route_ClientAccessStandingDesc</descriptionKey>
        <projectDefName>RR_GateStandingConnection</projectDefName>
      </li>
      <li>
        <kind>Purchase</kind>
        <labelKey>RR_Route_ClientAccessPartsLabel</labelKey>
        <descriptionKey>RR_Route_ClientAccessPartsDesc</descriptionKey>
        <thingDefName>ComponentIndustrial</thingDefName>
        <count>40</count>
      </li>
    </successRoutes>
  </RimroomsAsyncIndustries.Company.RimroomsRequestDef>
"""

KEY_BLOCK = u"""
  <!-- Arc 4 generated families. A route label is a thing the player picks and carries no full
       stop; a route description is prose and ends a sentence. -->

  <RR_Route_ClientSurveyFileLabel>File the record you already have</RR_Route_ClientSurveyFileLabel>
  <RR_Route_ClientSurveyFileDesc>A completed route log is the paperwork, and it stays the paperwork after the crew who wrote it are gone. Analyse a record and the client gets what they paid for.</RR_Route_ClientSurveyFileDesc>
  <RR_Route_ClientSurveySpeakLabel>Put someone who was there in front of them</RR_Route_ClientSurveySpeakLabel>
  <RR_Route_ClientSurveySpeakDesc>An employee who walked it and is still on the books can simply tell them. Cheaper than analysis and worth nothing the day that person leaves.</RR_Route_ClientSurveySpeakDesc>

  <RR_Route_ClientSamplesRecoverLabel>Bring it out yourself</RR_Route_ClientSamplesRecoverLabel>
  <RR_Route_ClientSamplesRecoverDesc>Haul the metal home and let it sit where the company can see it. The slow way, and the one that leaves the branch knowing a route it did not know before.</RR_Route_ClientSamplesRecoverDesc>
  <RR_Route_ClientSamplesBuyLabel>Order it and say nothing</RR_Route_ClientSamplesBuyLabel>
  <RR_Route_ClientSamplesBuyDesc>The catalogue sells metal. The buyer is not going to test it, the company has already worked that out, and neither of them will mention it again.</RR_Route_ClientSamplesBuyDesc>

  <RR_Route_ClientInstrumentsPlaceLabel>Set markers down and leave them</RR_Route_ClientInstrumentsPlaceLabel>
  <RR_Route_ClientInstrumentsPlaceDesc>Glow pods where the readings are wanted, and the company counts them as instruments. Nobody has to stay with them, which is the entire appeal.</RR_Route_ClientInstrumentsPlaceDesc>
  <RR_Route_ClientInstrumentsMethodLabel>Sell them the method instead</RR_Route_ClientInstrumentsMethodLabel>
  <RR_Route_ClientInstrumentsMethodDesc>Finish the second-reading work and the company has something it can licence to this client and the next one. More valuable to it than the readings ever were.</RR_Route_ClientInstrumentsMethodDesc>

  <RR_Route_ClientRescueTrainingLabel>Train people to go in after them</RR_Route_ClientRescueTrainingLabel>
  <RR_Route_ClientRescueTrainingDesc>Complete the rescue work and the branch has a capability rather than a favour. The company would rather own this than be owed it.</RR_Route_ClientRescueTrainingDesc>
  <RR_Route_ClientRescueAccountLabel>Have somebody say what is in there</RR_Route_ClientRescueAccountLabel>
  <RR_Route_ClientRescueAccountDesc>An employee who has seen one of the things that live down there, and is still here to describe it, closes this without anybody going back in.</RR_Route_ClientRescueAccountDesc>

  <RR_Route_ClientAccessStandingLabel>Make the connection hold</RR_Route_ClientAccessStandingLabel>
  <RR_Route_ClientAccessStandingDesc>Finish the standing-connection work. The client gets a door that behaves like a door, and the branch gets to stop treating every opening as an event.</RR_Route_ClientAccessStandingDesc>
  <RR_Route_ClientAccessPartsLabel>Hand over the parts and let them try</RR_Route_ClientAccessPartsLabel>
  <RR_Route_ClientAccessPartsDesc>Order the components and pass the problem along. Faster, and it teaches the branch nothing it will not have to learn later anyway.</RR_Route_ClientAccessPartsDesc>
"""


def append_before_close(path, anchor, block, guard):
    s = io.open(path, encoding='utf-8-sig').read()
    assert anchor in s, '%s: closing tag not found' % path
    assert guard not in s, '%s: block already applied' % path
    s = s.replace(anchor, block + anchor, 1)
    io.open(path, 'w', encoding='utf-8-sig', newline='').write(s)
    print('updated %s' % os.path.basename(path))


append_before_close(DEFS, u'\n</Defs>', DEF_BLOCK, u'RR_Request_ClientSurvey')
append_before_close(KEYED, u'\n</LanguageData>', KEY_BLOCK, u'RR_Route_ClientSurveyFileLabel')
