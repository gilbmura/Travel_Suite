# Security Considerations for Travel Suite

This document outlines security considerations and best practices for deploying Travel Suite in production. 

## Environment Variables

**Never commit sensitive credentials to version control.**

- Store all sensitive values in environment variables
- Use `.env` files for local development (and ensure they're in `.gitignore`)
- Use secure secret management services in production (AWS Secrets Manager, HashiCorp Vault, etc.)
- Rotate secrets regularly

### Required Environment Variables

- `SECRET_KEY`: Django secret key (generate a new, unique one for production)
- `DATABASE_PASSWORD`: MySQL database password
- `TWILIO_SID`, `TWILIO_TOKEN`: Twilio API credentials
- `EMAIL_HOST_PASSWORD`: SMTP password
- Payment provider API keys (when moving to live mode)

## HTTPS

**Always use HTTPS in production.**

- Configure SSL/TLS certificates (Let's Encrypt, AWS Certificate Manager, etc.)
- Redirect all HTTP traffic to HTTPS
- Set `SECURE_SSL_REDIRECT = True` in Django settings
- Use `SECURE_PROXY_SSL_HEADER` if behind a reverse proxy
- Set secure cookie flags: `SESSION_COOKIE_SECURE = True`, `CSRF_COOKIE_SECURE = True`

## Database Security

- Use strong, unique database passwords
- Restrict database access to application servers only
- Use connection encryption (SSL) for database connections
- Regularly backup databases
- Keep MySQL updated with security patches
- Use least-privilege database users

## API Security

### Rate Limiting

Implement rate limiting to prevent abuse:

```python
# Example using django-ratelimit
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='10/m', method='POST')
def create_booking(request):
    ...
```

Consider using:
- Django REST Framework throttling classes
- Third-party services (Cloudflare, AWS WAF)
- Nginx rate limiting

### Authentication & Authorization

- Use strong password policies for operators/admins
- Implement account lockout after failed login attempts
- Use token-based authentication with expiration
- Regularly rotate API tokens
- Implement role-based access control (RBAC)

### Input Validation

- Validate all user inputs on both client and server side
- Use Django forms and DRF serializers for validation
- Sanitize inputs to prevent SQL injection, XSS attacks
- Validate phone numbers, emails, and other formats

## Payment Security

### Idempotency Keys

- Always use idempotency keys for payment transactions
- Store idempotency keys in database with unique constraints
- Reject duplicate requests with the same idempotency key

### Webhook Validation

When implementing payment provider webhooks:

- Verify webhook signatures using provider's secret key
- Validate webhook payload structure
- Implement idempotent webhook handlers
- Log all webhook events for audit

### PCI Compliance

- Never store full credit card numbers
- Use payment provider tokens when possible
- Follow PCI DSS guidelines if handling card data directly

## Overbooking Prevention

The system uses database-level locking (`select_for_update`) to prevent overbooking:

- Always use transactions when creating bookings
- Lock schedule occurrences during booking creation
- Verify seat availability after acquiring lock

## Data Protection

### Personal Data

- Encrypt sensitive personal data at rest
- Use HTTPS for data in transit
- Implement data retention policies
- Comply with GDPR/local data protection regulations
- Allow users to request data deletion

### Logging

- Don't log sensitive information (passwords, payment details)
- Use structured logging
- Rotate log files regularly
- Monitor logs for suspicious activity

## Session Security

- Use secure, HTTP-only cookies
- Set appropriate session timeout
- Regenerate session ID on login
- Use CSRF protection (Django provides this by default)

## CORS Configuration

- Restrict CORS allowed origins to specific domains
- Don't use wildcard (`*`) in production
- Configure CORS headers appropriately

## Dependency Management

- Regularly update dependencies for security patches
- Use `pip-audit` or similar tools to check for vulnerabilities
- Pin dependency versions in `requirements.txt`
- Review and audit third-party packages

## Monitoring & Alerting

- Monitor failed login attempts
- Alert on unusual payment patterns
- Track API error rates
- Monitor database performance
- Set up alerts for security events

## Backup & Recovery

- Regular automated database backups
- Test backup restoration procedures
- Store backups in secure, encrypted locations
- Implement disaster recovery plan

## Production Checklist

- [ ] Change `DEBUG = False` in production
- [ ] Set `ALLOWED_HOSTS` to specific domains
- [ ] Use strong `SECRET_KEY`
- [ ] Enable HTTPS
- [ ] Configure secure cookies
- [ ] Set up rate limiting
- [ ] Enable database SSL
- [ ] Configure secure email (TLS/SSL)
- [ ] Set up monitoring and alerting
- [ ] Configure backup strategy
- [ ] Review and restrict CORS
- [ ] Update all dependencies
- [ ] Review Django security settings
- [ ] Set up log rotation
- [ ] Configure firewall rules
- [ ] Enable database connection pooling
- [ ] Set up error tracking (Sentry, etc.)

## Additional Resources

- [Django Security Documentation](https://docs.djangoproject.com/en/stable/topics/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)

