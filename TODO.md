## 📋 Project Finalization Checklist

### 🛠 Development: Issues to be Resolved

- [ ] **Database Optimization:** Decide on the usage of `INDEX` and `VIEW`.

- [ ] **Schema Validation:** Conduct a final review of the database schema for logic and consistency.

- [ ] **Admin Panel:** Identify and fix any missing features or bugs in the admin interface.

- [ ] **Assets:** Verify if the final versions of all photos/images are sufficient.

- [ ] **Data Integrity:** Identify any remaining synthetic data and replace it if necessary.

---

## 🎤 Presentation Requirements

- [ ] **PPT Preparation:** Design the PowerPoint file (Max **10 minutes** duration).

- [ ] **Team Roles:** Include photos, names, and specific roles for **every member**.

- [ ] **Project Overview:** Define the application’s purpose, motivation, and goals.

- [ ] **Database Design:**
  
  - [ ] Create the **ER Diagram** (using the visual notation learned in class).
  
  - [ ] Document the **Relational Schema transformation**.
  
  - [ ] Explain the **Normalization process** (Show Before/After tables and justify 3NF or BCNF).

- [ ] **Dataset Details:** Document the content, source, size, and any scraping/parsing/synthetic methods used.

- [ ] **App Showcase:** Include screenshots of features alongside their **complex SQL queries** (JOINs, Subqueries, GROUP BY, etc.).

- [ ] **Testing:** Provide a general summary of the tests performed.

- [ ] **Speaking Parts:** Ensure **every team member** has a designated speaking slot.

---

## 💻 Demo Requirements

- [ ] **Time Management:** Ensure the demo fits within the **20-25 minute** total window.

- [ ] **Table Ownership:** Each member must explain their responsible **Main Tables**, including:
  
  - [ ] Primary Keys (PK) and Foreign Keys (FK).
  
  - [ ] Functional **CRUD operations** (Create, Read, Update, Delete).

- [ ] **Technical Deep Dive:** Show the ER Diagram/Relational Schema and UI components.

- [ ] **Advanced SQL:** Each member must present at least one **advanced/nested query** (Aggregate, JOIN, or Subquery).

- [ ] **Q&A Readiness:** Every member must be prepared to answer theoretical questions on database concepts.

---

## 📄 Report & Submission (The Final Stretch)

- [ ] **Format:** Convert the presentation slides to **PDF**.

- [ ] **Packaging:** Create a **.zip** file (Maximum size: **50 MB**).

- [ ] **Deadline:** Aim to finish everything by **Sunday evening**.

- [ ] **Individual Action:** Remind every member to **upload the file individually** by Monday morning.

---

> **Note:** Since the deadline is Monday morning, prioritize the **Normalization documentation** and **Advanced SQL queries** today, as these usually take the most time to explain clearly. 

---

- [ ] Discuss the possibility of deploying the project as a web app to the cloud
  
  ## Completed

> Items are listed from most recent to earliest.

- [x] Home page needs to be rendered as an html page, should not return a basic json response
- [x] Upload Actors' & Directors' photos, some actors may be disregarded for convenience (~29850 people total)
- [x] Review the layout of Nexus page
- [x] Files inside init-db folder should be grouped for better project structure
- [x] Build a simple front-end to make testing easier
- [x] Ensure database tables are defined without logic errors and then populate tables
- [x] Test endpoints with curl, Postman etc.
- [x] SQL queries' creation logic must be determined. Inline or modular? -- Modular
- [x] Update/Create API endpoints -- Everybody started adding new endpoints
- [x] Add table definition queries for PostgreSQL
- [x] Decide on the PostgreSQL version (using: version 15, available: version 18) -- Decided to use version 17 for better stability
- [x] Update/Create README.md to be more detailed
