# Product Caching Strategy

## Key Pattern
`product:{product_id}`

## TTL
60 seconds.

Reason: The response include `price` (which can change via `PUT` /products/{id}) and `average_rating`/`review_count` (which update whenever a new review is posted) - both of which change more frequently → proactive invalidation is the primary mechanism.