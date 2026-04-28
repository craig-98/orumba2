-- Run this in your Supabase SQL Editor (https://supabase.com/dashboard/project/_/sql)

-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- Users table
create table if not exists users (
    id serial primary key,
    username text unique not null,
    password text not null,
    role text default 'citizen',
    name text,
    email text,
    avatar text
);

-- Posts table
create table if not exists posts (
    id serial primary key,
    user_id integer references users(id),
    title text,
    content text,
    category text default 'general',
    image text,
    status text default 'draft',
    created_at text,
    published_at text,
    author text
);

-- Events table
create table if not exists events (
    id serial primary key,
    user_id integer references users(id),
    title text,
    content text,
    date text,
    location text,
    status text default 'draft',
    created_at text
);

-- Albums table
create table if not exists albums (
    id serial primary key,
    user_id integer references users(id),
    title text,
    posts jsonb default '[]'::jsonb
);

-- Enable Row Level Security (optional but recommended)
alter table users enable row level security;
alter table posts enable row level security;
alter table events enable row level security;
alter table albums enable row level security;

-- Allow public read access
create policy "Allow public read" on users for select using (true);
create policy "Allow public read" on posts for select using (true);
create policy "Allow public read" on events for select using (true);
create policy "Allow public read" on albums for select using (true);

-- Allow authenticated insert/update/delete (simplified)
create policy "Allow all operations" on users for all using (true) with check (true);
create policy "Allow all operations" on posts for all using (true) with check (true);
create policy "Allow all operations" on events for all using (true) with check (true);
create policy "Allow all operations" on albums for all using (true) with check (true);
