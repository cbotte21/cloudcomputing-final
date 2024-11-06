// app/routes/results.tsx
import { Box, Button, Divider, Grid2, TextField, Typography } from "@mui/material";
import { Form, Link, MetaFunction, useLoaderData } from "@remix-run/react";
import { json, redirect } from "@remix-run/server-runtime";
import Index from "./_index";

export const loader = async ({ request }: any) => {
  const username = process.env.USERNAME;
  const password = process.env.PASSWORD;
  const opensearchDomain = process.env.DOMAIN;

  const url = new URL(request.url);
  const query = url.searchParams.get("q");

  if (!query) {
    return json({ results: [] });
  }

  const opensearchUrl = `${opensearchDomain}?q=${encodeURIComponent(query)}`;

  try {
    const response = await fetch(opensearchUrl, {
      method: 'GET',
      headers: {
        'Authorization': 'Basic ' + btoa(`${username}:${password}`),
        'Content-Type': 'application/json',
      }
    });
    const data = await response.json();
    const results = data.hits.hits.map((hit: any) => hit._source) ?? [];
    return json({ results: {
      sites: results,
      defaultQuery: query
    } });
  } catch (error) {
    console.error("Error fetching data from OpenSearch:", error);
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