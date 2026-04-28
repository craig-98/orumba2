# Supabase Migration Plan

## Steps
- [x] 1. Analyze current data models (posts, users, events, albums)
- [x] 2. Add `supabase` to requirements.txt
- [x] 3. Create `app/db.py` with Supabase client wrapper + JSON fallback
- [x] 4. Refactor app.py to use db.py (all routes preserved)
- [x] 5. Create SQL schema for Supabase tables
- [ ] 6. Create Supabase project and run SQL
- [ ] 7. Add env vars to Vercel dashboard
- [ ] 8. Deploy and test

## How it works
- **Locally**: No Supabase credentials = automatically uses JSON files (same as before)
- **On Vercel**: Set `SUPABASE_URL` and `SUPABASE_KEY` = uses PostgreSQL database (data persists)

## Files changed
- `requirements.txt` — added `supabase==2.15.0`
- `app.py` — replaced JSON load/save with `app.db` calls
- `app/db.py` — new unified database layer
- `supabase_schema.sql` — SQL to create tables in Supabase
- `vercel.json` — already updated for Vercel deployment
- `api/index.py` — already updated for Vercel entry point

## Next steps for you
1. Go to https://supabase.com and create a new project
2. In the SQL Editor, run the contents of `supabase_schema.sql`
3. In your Vercel project dashboard, add Environment Variables:
   - `SUPABASE_URL` = your Supabase project URL
   - `SUPABASE_KEY` = your Supabase anon/public key
   - `SECRET_KEY` = any random string
4. Deploy: `vercel --prod`
