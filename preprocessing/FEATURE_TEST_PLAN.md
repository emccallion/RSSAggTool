# News Preprocessing System - Feature Test Plan

## App Overview
Django-based news article preprocessing and curation system with RSS feed aggregation.

## Core Features (Based on Code Review)

### 1. Article Management
**Endpoints:**
- `/` - Article list view with filtering and sorting
- `/article/<id>/` - Article detail view

**Claimed Features:**
- [x] View all preprocessing articles in paginated list (20 per page)
- [x] Filter articles by:
  - Outcome (NEW, processed, rejected)
  - Source (e.g., Financial Times, Bloomberg)
  - Story group
  - Search term (title/description)
  - Added by
- [x] Sort articles by 10 different options:
  - Newest first / Oldest first (time_added)
  - Published date (newest/oldest)
  - Source (A-Z / Z-A)
  - Outcome (A-Z / Z-A)
  - Story group (A-Z / Z-A)
- [x] View article statistics (total, new, processed, rejected)
- [x] Bulk actions on selected articles:
  - Mark as processed
  - Mark as rejected
  - Mark as NEW
  - Assign to story group
- [x] Article detail page with full content
- [x] Edit article (outcome, storygroup, modified_by)
- [x] AJAX quick edit for individual fields

**To Test:**
1. Article list displays correctly
2. All filters work
3. All sort options work
4. Bulk actions work
5. Article detail page loads
6. Edit form works
7. AJAX quick edit works

---

### 2. RSS Feed Management
**Endpoints:**
- `/feeds/` - Feed list view
- `/feeds/add/` - Add new feed
- `/feeds/<id>/edit/` - Edit feed
- `/feeds/<id>/toggle/` - Toggle active status

**Claimed Features:**
- [x] View all RSS feeds in database
- [x] Filter feeds by:
  - Active status (active/inactive/all)
  - Source name
  - Category
- [x] Feed statistics (total, active, inactive)
- [x] Add new RSS feed through web form
- [x] Edit existing feeds
- [x] Toggle feed active/inactive status
- [x] 10 category choices available
- [x] Django admin interface for feeds

**To Test:**
1. Feed list displays correctly
2. Filters work
3. Add new feed form works
4. Edit feed form works
5. Toggle active status works
6. Only active feeds are fetched by aggregator

---

### 3. Article Sync/Aggregation
**Endpoints:**
- `/sync/` - Sync status and control page

**Claimed Features:**
- [x] Fetch articles from all active RSS feeds
- [x] Parse RSS feeds with feedparser
- [x] Classify articles by topic (10 topics via keyword matching)
- [x] Analyze article sentiment (positive/negative/neutral)
- [x] Automatic duplicate detection (title + source + published date)
- [x] Set outcome="NEW" for all fetched articles
- [x] Set added_by="SYSTEM" for automated imports
- [x] Display fetch statistics
- [x] Integration with Django ORM (single database)

**To Test:**
1. Sync page loads and shows statistics
2. Fetch button works
3. Articles are fetched and classified
4. Duplicates are skipped
5. New articles appear with outcome=NEW
6. Statistics update after fetch

---

### 4. Admin Interface
**Endpoints:**
- `/admin/` - Django admin

**Claimed Features:**
- [x] Article admin with filters and search
- [x] Feed admin with filters and search
- [x] Bulk actions in admin

**To Test:**
1. Admin login works
2. Article admin accessible
3. Feed admin accessible
4. Filters and search work

---

## Frontend/UX Features

**Navigation:**
- [x] Main navbar with links (Articles, Sync, RSS Feeds, Admin)
- [x] Bootstrap 5 responsive design
- [x] Bootstrap Icons

**Display:**
- [x] Statistics cards/dashboards
- [x] Color-coded outcome badges
- [x] Pagination controls
- [x] Success/error messages
- [x] Form validation

**To Review for Design:**
1. Overall layout and spacing
2. Color scheme and consistency
3. Typography and readability
4. Button styles and hierarchy
5. Card designs
6. Table formatting
7. Form layouts
8. Mobile responsiveness
9. Professional appearance
10. Modern vs dated look

---

## Test Results

### Article Management Tests
- [ ] List view loads
- [ ] Filters work correctly
- [ ] Sort options work correctly
- [ ] Bulk actions work
- [ ] Detail view loads
- [ ] Edit functionality works
- [ ] Statistics accurate

### Feed Management Tests
- [ ] List view loads
- [ ] Add feed works
- [ ] Edit feed works
- [ ] Toggle status works
- [ ] Filters work
- [ ] Statistics accurate

### Sync Tests
- [ ] Sync page loads
- [ ] Fetch articles works
- [ ] Classification works
- [ ] Duplicate detection works
- [ ] Statistics update

### Admin Tests
- [ ] Admin accessible
- [ ] Article admin works
- [ ] Feed admin works

### Design Review
- [ ] Navigation clear and consistent
- [ ] Color scheme professional
- [ ] Typography readable
- [ ] Spacing appropriate
- [ ] Forms user-friendly
- [ ] Mobile responsive
- [ ] Modern appearance
