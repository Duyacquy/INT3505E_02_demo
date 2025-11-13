Subject: [ACTION REQUIRED] Payment API v1 Deprecation Notice - Please Migrate to v2

Hello Developers,

This is an official notice that our Payment API version 1 (v1), specifically the endpoint `POST /v1/charge`, is now deprecated.

We are launching our new Payment API v2 (`POST /v2/payments`), which offers enhanced security via tokenization, better performance, and support for more payment methods.

This change is a breaking change, as the new v2 API requires a `payment_token` instead of direct card details.

== Deprecation Timeline ==

* **Deprecation Date:** November 12, 2025
* **Sunset Date (End of Life):** May 12, 2026

== Action Required ==

To avoid any service disruption, you must migrate your application from API v1 to API v2 before the **Sunset Date (May 12, 2026)**.

After this date, all requests to the `v1/charge` endpoint will fail, returning a `410 Gone` error.

== Resources ==

We have prepared resources to make this transition as smooth as possible:

1.  **New API v2 Documentation:** [Link to your v2 API Docs]
2.  **v1-to-v2 Migration Guide:** [Link to your Migration Guide]

We strongly recommend starting the migration process soon. If you have any questions or require assistance, please contact our developer support team at [support@example.com] or visit our community forum [Link to Forum].

We apologize for any inconvenience this may cause and are confident that API v2 will provide a much better and more secure experience.

Thank you,
The API Team