# Cloudflare

Using cloudflare has a couple of benefits. Firstly, Backblaze notes that 
"Downloads through our CDN and Compute partners are also free."[[0](https://www.backblaze.com/b2/cloud-storage-pricing.html)]
So by proxying requests through Cloudflare, we shouldn't ever have to pay download fees to Backblaze.

Secondally, we can have a "pretty" url. An example friendly URL that Backblaze provides looks like this:

`https://f000.backblazeb2.com/file/<BUCKET_NAME>/<FILENAME>`

Following the steps below, allow us to change that to:

`https://<CUSTOM_DOMAIN>/<FILENAME>`

## DNS

Set the name to the subdomain you want to serve files from. The example below would 
be https://b2.example.com.  

The domain for the content field is obtained from the friendly url of an uploaded file.  

We want to proxy the requests to save on download costs.

```
Type    Name    Content                 TTL     Proxy Status
CNAME   b2      f000.backblazeb2.com    Auto    Proxied
```

## Rules

1 - https://<PRETTY_URL>/file/<BUCKET_NAME>/*
Cache Level: Bypass

2 - https://<PRETTY_URL>/file/*/*
Forwarding URL (Status Code: 302 - Temporary Redirect, Url: https://<PRETTY_URL>/404)



## Worker

Set the route to <PRETTY_URL>/*

```javascript
async function handleRequest(request) {
    let url = new URL(request.url)
    // make sure you set B2_BUCKET_NAME as an environment variable
    url.pathname = `/file/${B2_BUCKET_NAME}${url.pathname}`

    let modified = new Request(url.toString(), request)
    let response = await fetch(modified)

    // Recreate the response so we can modify the headers
    response = new Response(response.body, response)

    // Set CORS headers
    response.headers.set("Access-Control-Allow-Origin", "*")

    // Append to/Add Vary header so browser will cache response correctly
    response.headers.append("Vary", "Origin")

    return response
}

addEventListener('fetch', event => {
    event.respondWith(handleRequest(event.request))
})
```