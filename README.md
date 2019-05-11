# easyQuest

Easily check application statuses on quest using Python requests.

### Prerequisites
- Python 3  
- Requests  
- Beautiful Soup  
- lxml

## Setup
Save login creditials in config.json

```
a = Application(username, password)
a.get_appstatus()
```
Returns a dictionary
```
{
    "Program": "Status"
}
```
Since Quest times out, the timer can be reset.
```
a.reset_timeout()
```

