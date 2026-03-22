# Email hook

Send alert to smtp

## Config 

```yaml
webhooks:
    email_hook:
        type: email # required
        host: smtp.gmail.com # required
        port: 587 # optional default(587)
        username: 'user' # required
        password: 'pass' # required
        from: 'from' # required
        to: 'to' # required
        use_tls: true # optional default(false)
        subject: 'sub' # optional default('[ALERT] ClickDetect')
        template: '{{ rule.name }}' # optional default(DEFAULT_TEMPLATE)
```
