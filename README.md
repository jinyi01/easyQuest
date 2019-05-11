# easyQuest

Tool to easily check application status on quest.

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