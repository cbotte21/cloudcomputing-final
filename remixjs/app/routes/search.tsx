// app/routes/results.tsx
import { Divider, Grid2, Typography } from "@mui/material";
import { Link, MetaFunction, useLoaderData } from "@remix-run/react";
import { json } from "@remix-run/server-runtime";
import Index from "./_index";
import {pool} from "../pool.server.js"

export const loader = async ({ request }: any) => {
  // Dynamically import 'pg' only on the server
  if (typeof window !== "undefined") {
    return json({ results: [] }); // Return empty if it's a client-side request
  }

  const url = new URL(request.url);
  const query = url.searchParams.get("q");

  if (!query) {
    return json({ results: [] });
  }

  try {
    const result = await pool.query(
      "SELECT * FROM your_table_name WHERE title ILIKE $1 OR description ILIKE $1 OR title ILIKE $1 OR content ILIKE $1 LIMIT 20",
      [`%${query}%`] // Parameterized query to prevent SQL injection
    );

    return json({
      results: {
        sites: result.rows,
        defaultQuery: query,
      },
    });
  } catch (error) {
    console.error("Error querying PostgreSQL:", error);
    return json({ results: [] });
  }
};

// Meta function for SEO
export const meta: MetaFunction = () => [
  { title: 'Remix Starter - Results' },
  { name: 'description', content: 'Search results from RDS' },
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