# Use Case Diagram

```mermaid
flowchart LR
    Reader([Reader])
    Journalist([Journalist])
    Editor([Editor])

    UC1((Register Account))
    UC2((Login))
    UC3((Browse Approved Articles))
    UC4((View Article Details))
    UC5((Subscribe to Publisher))
    UC6((Subscribe to Journalist))
    UC7((View Subscribed Articles))
    UC8((Create Article))
    UC9((Edit Own Article))
    UC10((Submit Article for Review))
    UC11((Review Pending Articles))
    UC12((Approve Article))
    UC13((Reject Article))
    UC14((Access Dashboard))

    Reader --> UC1
    Reader --> UC2
    Reader --> UC3
    Reader --> UC4
    Reader --> UC5
    Reader --> UC6
    Reader --> UC7
    Reader --> UC14

    Journalist --> UC1
    Journalist --> UC2
    Journalist --> UC3
    Journalist --> UC4
    Journalist --> UC8
    Journalist --> UC9
    Journalist --> UC10
    Journalist --> UC14

    Editor --> UC1
    Editor --> UC2
    Editor --> UC3
    Editor --> UC4
    Editor --> UC8
    Editor --> UC9
    Editor --> UC11
    Editor --> UC12
    Editor --> UC13
    Editor --> UC14