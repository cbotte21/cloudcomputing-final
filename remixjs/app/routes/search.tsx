// app/routes/results.tsx
  import { Box, Button, Divider, Grid2, TextField, Typography } from "@mui/material";
  import { Form, Link, MetaFunction, useLoaderData } from "@remix-run/react";
  import { json, redirect } from "@remix-run/server-runtime";
  import Index from "./_index";

  // export const loader = async ({ request }: any) => {
    // const username = process.env.USERNAME;
    // const password = process.env.PASSWORD;
    // const opensearchDomain = process.env.DOMAIN;

    // TODO: Get environment variables for rds
    // TODO: Connect to rds
    // TODO: Query rds
    // Return response

    export const loader = async ({ request }: any) => {
      const postgrestUrl = process.env.POSTGREST_URL;
      const postgrestApiKey = process.env.POSTGREST_API_KEY;
    
      if (!postgrestUrl) {
        throw new Error("PostgREST URL is not configured.");
      }
    
      const url = new URL(request.url);
      const query = url.searchParams.get("q");
    
      if (!query) {
        return json({ results: [] });
      }
    
      // Make a request to PostgREST to search for data
      try {
        const response = await fetch(`${postgrestUrl}/sites?title=ilike.%${encodeURIComponent(query)}%`, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${postgrestApiKey}`,
          },
        });
    
        if (!response.ok) {
          console.error("Failed to fetch data from PostgREST:", response.statusText);
          return json({ results: [] });
        }
    
        const data = await response.json();
        return json({
          results: {
            sites: data,
            defaultQuery: query,
          },
        });
      } catch (error) {
        console.error("Error connecting to PostgREST:", error);
        return json({ results: [] });
      }
    };

  // Meta function for SEO
  export const meta: MetaFunction = () => [
    { title: 'Remix Starter - Results' },
    { name: 'description', content: 'Search results from OpenSearch' },
  ];

  export default function Search() {
    const { results }: any = useLoaderData();
    const sites = results["sites"] ?? []
    const defaultQuery = results["defaultQuery"]

    return (
      <Grid2 container direction="column">
          <Grid2>
            <Index defaultQuery={defaultQuery} />
          </Grid2>
          <Divider />
          <Grid2>
            {sites.length === 0 ? (
                <Typography>No results found.</Typography>
            ) : 
                <Grid2 container direction="column" spacing={2} sx={{ paddingX: 10, paddingTop: 3 }}>
                  {sites.map((result: any, index: number) => (
                    <Grid2 container direction="column" key={index}>
                      <Link to={result.url}>
                        <Typography variant="h4">
                          {result.title}
                        </Typography>
                      </Link>
                      <Typography variant="body2">
                        {result.description}
                      </Typography>
                    </Grid2>
                  ))}
                </Grid2>
            }
          </Grid2>
        </Grid2>
    );
  }