
import React, { useEffect, useMemo, useState } from "react";
import {
  BookOpen, LayoutDashboard, Users, ArrowLeftRight, Library, Wallet,
  Settings, LogOut, Search, Plus, RefreshCw, Menu, X, GraduationCap,
  ShieldCheck, FileUp, Eye, RotateCcw, KeyRound, UserRound, BookMarked,
  AlertCircle, CheckCircle2, ChevronRight, Sparkles
} from "lucide-react";

import {
  api, get, post, put, saveSession, clearSession, getToken, getRole, getBlob
} from "./api";

const money = (paise) => `₹${(Number(paise || 0) / 100).toFixed(2)}`;

const asArray = (value) =>
  Array.isArray(value) ? value :
  Array.isArray(value?.value) ? value.value :
  Array.isArray(value?.items) ? value.items :
  Array.isArray(value?.policies) ? value.policies :
  Array.isArray(value?.borrowings) ? value.borrowings :
  Array.isArray(value?.digital_books) ? value.digital_books :
  Array.isArray(value?.fines) ? value.fines :
  [];

const errorText = (e) => e?.message || "Something went wrong. Please try again.";

function App() {
  const [token, setToken] = useState(getToken());
  const [role, setRole] = useState(getRole());
  const [profile, setProfile] = useState(null);
  const [page, setPage] = useState("dashboard");
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState(null);
  const [mobileOpen, setMobileOpen] = useState(false);

  const notify = (message, type = "success") => {
    setNotice({ message, type });
    window.setTimeout(() => setNotice(null), 4500);
  };

  useEffect(() => {
    if (!token) return;

    get("/auth/me")
      .then((data) => {
        setProfile(data);
        setRole(data.role);
        localStorage.setItem("library360_role", data.role);
      })
      .catch((e) => {
        clearSession();
        setToken(null);
        setRole(null);
        setProfile(null);
        notify(errorText(e), "error");
      });
  }, [token]);

  const logout = () => {
    clearSession();
    setToken(null);
    setRole(null);
    setProfile(null);
    setPage("dashboard");
  };

  const login = async (identifier, password, selectedRole) => {
    setBusy(true);

    try {
      const data = await post(`/auth/${selectedRole}/login`, {
        identifier,
        password
      });

      saveSession(data.access_token, data.role);
      setToken(data.access_token);
      setRole(data.role);

      const me = await get("/auth/me");
      setProfile(me);
      setPage("dashboard");

      notify(`Welcome, ${me.full_name || "to Library360"}!`);
    } catch (e) {
      notify(errorText(e), "error");
    } finally {
      setBusy(false);
    }
  };

  if (!token || !profile) {
    return <Login onLogin={login} busy={busy} notice={notice} />;
  }

  return (
    <div className="app-shell">
      <aside className={`sidebar ${mobileOpen ? "open" : ""}`}>
        <div className="brand">
          <div className="brand-mark"><Library size={22} /></div>
          <div>
            <strong>Library<span>360</span></strong>
            <small>KNOWLEDGE, CONNECTED</small>
          </div>
          <button className="icon-btn mobile-close" onClick={() => setMobileOpen(false)}>
            <X />
          </button>
        </div>

        <div className="side-label">WORKSPACE</div>

        <nav>
          <NavItem icon={<LayoutDashboard />} label="Dashboard" active={page === "dashboard"} onClick={() => { setPage("dashboard"); setMobileOpen(false); }} />
          <NavItem icon={<BookOpen />} label="Books" active={page === "books"} onClick={() => { setPage("books"); setMobileOpen(false); }} />

          {role === "librarian" ? (
            <>
              <div className="side-label nav-gap">LIBRARY OPERATIONS</div>
              <NavItem icon={<Users />} label="Students" active={page === "students"} onClick={() => { setPage("students"); setMobileOpen(false); }} />
              <NavItem icon={<ArrowLeftRight />} label="Borrowing desk" active={page === "borrowing"} onClick={() => { setPage("borrowing"); setMobileOpen(false); }} />
              <NavItem icon={<BookMarked />} label="Digital access" active={page === "digital"} onClick={() => { setPage("digital"); setMobileOpen(false); }} />
              <NavItem icon={<Wallet />} label="Fines" active={page === "fines"} onClick={() => { setPage("fines"); setMobileOpen(false); }} />
              <NavItem icon={<Settings />} label="Policies" active={page === "policies"} onClick={() => { setPage("policies"); setMobileOpen(false); }} />
            </>
          ) : (
            <>
              <div className="side-label nav-gap">MY LIBRARY</div>
              <NavItem icon={<ArrowLeftRight />} label="My borrowings" active={page === "my-borrowings"} onClick={() => { setPage("my-borrowings"); setMobileOpen(false); }} />
              <NavItem icon={<BookMarked />} label="My digital books" active={page === "my-digital"} onClick={() => { setPage("my-digital"); setMobileOpen(false); }} />
              <NavItem icon={<Wallet />} label="My fines" active={page === "my-fines"} onClick={() => { setPage("my-fines"); setMobileOpen(false); }} />
            </>
          )}
        </nav>

        <div className="sidebar-bottom">
          <div className="secure-note">
            <ShieldCheck size={16} />
            <span>Signed in securely<br /><b>JWT authenticated</b></span>
          </div>
          <button className="logout-btn" onClick={logout}>
            <LogOut size={17} /> Sign out
          </button>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <button className="icon-btn mobile-menu" onClick={() => setMobileOpen(true)}>
            <Menu />
          </button>

          <div className="breadcrumb">
            Library360 <ChevronRight size={14} /> <b>{pageTitle(page)}</b>
          </div>

          <div className="top-user">
            <div className="user-avatar">
              {(profile.full_name || "U").slice(0, 1).toUpperCase()}
            </div>
            <div className="user-meta">
              <b>{profile.full_name}</b>
              <span>{role === "librarian" ? "Librarian" : `Student · ${profile.usn || profile.student_id || ""}`}</span>
            </div>
          </div>
        </header>

        <div className="content">
          {page === "dashboard" && <Dashboard profile={profile} role={role} go={setPage} />}
          {page === "books" && <Books role={role} notify={notify} />}
          {page === "students" && role === "librarian" && <Students notify={notify} />}
          {page === "borrowing" && role === "librarian" && <BorrowingDesk notify={notify} />}
          {page === "my-borrowings" && role === "student" && <StudentBorrowings profile={profile} />}
          {page === "digital" && role === "librarian" && <DigitalAdmin notify={notify} />}
          {page === "my-digital" && role === "student" && <StudentDigital profile={profile} />}
          {page === "fines" && role === "librarian" && <FineDesk notify={notify} />}
          {page === "my-fines" && role === "student" && <StudentFines profile={profile} />}
          {page === "policies" && role === "librarian" && <Policies notify={notify} />}
        </div>

        <footer className="footer">
          © 2026 Library360 <span>Library management, made simpler.</span>
        </footer>
      </main>

      {notice && (
        <div className={`toast ${notice.type}`}>
          <span>
            {notice.type === "error" ? <AlertCircle size={18} /> : <CheckCircle2 size={18} />}
          </span>
          {notice.message}
        </div>
      )}
    </div>
  );
}

function pageTitle(page) {
  return ({
    dashboard: "Dashboard",
    books: "Books",
    students: "Students",
    borrowing: "Borrowing desk",
    "my-borrowings": "My borrowings",
    digital: "Digital access",
    "my-digital": "My digital books",
    fines: "Fine management",
    "my-fines": "My fines",
    policies: "Borrowing policies"
  })[page] || "Dashboard";
}

function NavItem({ icon, label, active, onClick }) {
  return (
    <button className={`nav-item ${active ? "active" : ""}`} onClick={onClick}>
      {icon}<span>{label}</span>{active && <i />}
    </button>
  );
}

function Login({ onLogin, busy, notice }) {
  const [selectedRole, setSelectedRole] = useState("librarian");
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");

  const submit = (e) => {
    e.preventDefault();
    onLogin(identifier.trim(), password, selectedRole);
  };

  return (
    <div className="login-page">
      <div className="login-art">
        <div className="art-brand">
          <div className="brand-mark"><Library size={23} /></div>
          <strong>Library<span>360</span></strong>
        </div>

        <div className="art-copy">
          <div className="eyebrow"><Sparkles size={15} /> YOUR CAMPUS. YOUR KNOWLEDGE.</div>
          <h1>Every book.<br /><em>One place.</em></h1>
          <p>A smarter library experience for curious minds and the people who keep knowledge moving.</p>
          <div className="art-stats">
            <div><b>360°</b><span>Library access</span></div>
            <div><b>One</b><span>Connected space</span></div>
          </div>
        </div>

        <div className="art-decoration">
          <div className="book book-one" />
          <div className="book book-two" />
          <div className="book book-three" />
          <div className="circle-glow" />
        </div>

        <div className="art-foot">DISCOVER · LEARN · GROW</div>
      </div>

      <div className="login-panel">
        <div className="login-card">
          <div className="mobile-brand">
            <div className="brand-mark"><Library size={21} /></div>
            <strong>Library<span>360</span></strong>
          </div>

          <div className="login-kicker">WELCOME BACK</div>
          <h2>Sign in to your library</h2>
          <p className="muted">Choose your account type to continue.</p>

          <div className="role-switch">
            <button className={selectedRole === "librarian" ? "selected" : ""} onClick={() => setSelectedRole("librarian")}>
              <ShieldCheck size={17} /> Librarian
            </button>
            <button className={selectedRole === "student" ? "selected" : ""} onClick={() => setSelectedRole("student")}>
              <GraduationCap size={18} /> Student
            </button>
          </div>

          <form onSubmit={submit}>
            <label>{selectedRole === "librarian" ? "Email address" : "USN or email"}</label>
            <div className="field-wrap">
              <UserRound size={17} />
              <input
                required
                value={identifier}
                onChange={e => setIdentifier(e.target.value)}
                placeholder={selectedRole === "librarian" ? "you@library.edu" : "e.g. 1RV21CS001"}
              />
            </div>

            <label>Password</label>
            <div className="field-wrap">
              <KeyRound size={17} />
              <input
                required
                type="password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="Enter your password"
              />
            </div>

            <button className="primary-btn login-submit" disabled={busy}>
              {busy ? "Signing in…" : "Sign in"} <ChevronRight size={18} />
            </button>
          </form>

          <div className="login-security">
            <ShieldCheck size={15} /> Your session is protected with JWT authentication.
          </div>

          {notice && <div className={`inline-alert ${notice.type}`}>{notice.message}</div>}
        </div>

        <div className="login-copyright">© 2026 Library360 · Built for better learning</div>
      </div>
    </div>
  );
}

function PageHeading({ eyebrow, title, subtitle, action }) {
  return (
    <div className="page-heading">
      <div>
        <div className="eyebrow">{eyebrow}</div>
        <h1>{title}</h1>
        {subtitle && <p>{subtitle}</p>}
      </div>
      {action}
    </div>
  );
}

function Stat({ icon, label, value, tone = "blue", hint }) {
  return (
    <div className="stat-card">
      <div className={`stat-icon ${tone}`}>{icon}</div>
      <div>
        <span>{label}</span>
        <strong>{value}</strong>
        {hint && <small>{hint}</small>}
      </div>
    </div>
  );
}

function Dashboard({ profile, role, go }) {
  const [books, setBooks] = useState([]);
  const [myData, setMyData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    get("/books/")
      .then(d => setBooks(asArray(d)))
      .catch(() => {})
      .finally(() => setLoading(false));

    if (role === "student" && profile.student_id) {
      get(`/borrowings/student/${encodeURIComponent(profile.student_id)}`)
        .then(d => setMyData(asArray(d)))
        .catch(() => {});
    }
  }, [role, profile.student_id]);

  const active = myData.filter(x => x.status === "active" || x.status === "overdue").length;

  return (
    <>
      <PageHeading
        eyebrow={role === "librarian" ? "LIBRARIAN OVERVIEW" : "STUDENT OVERVIEW"}
        title={`Good day, ${(profile.full_name || "").split(" ")[0]} 👋`}
        subtitle={role === "librarian" ? "Here's what's happening across your library." : "Your personal library space, all in one place."}
      />

      <div className="welcome-banner">
        <div>
          <div className="banner-tag">LIBRARY360 · {role.toUpperCase()} PORTAL</div>
          <h2>{role === "librarian" ? "Knowledge starts with you." : "Your next great read awaits."}</h2>
          <p>{role === "librarian" ? "Manage your collection, support students and keep the library running smoothly." : "Explore the collection, keep track of your loans and access your digital shelf."}</p>
          <button className="banner-btn" onClick={() => go("books")}>
            Explore books <ChevronRight size={16} />
          </button>
        </div>
        <div className="banner-illustration">
          <div className="illu-circle"><BookOpen size={66} /></div>
          <div className="illu-spark">✦</div>
        </div>
      </div>

      <div className="stats-grid">
        <Stat icon={<BookOpen />} label="Books in collection" value={loading ? "—" : books.length} tone="blue" hint="Available catalogue" />

        {role === "student" ? (
          <>
            <Stat icon={<ArrowLeftRight />} label="My active loans" value={myData.length ? active : "—"} tone="violet" hint="Current borrowings" />
            <Stat icon={<GraduationCap />} label="My USN" value={profile.usn || profile.student_id || "—"} tone="green" hint="Login identifier" />
          </>
        ) : (
          <>
            <Stat icon={<Users />} label="Workspace" value="Ready" tone="green" hint="Librarian access active" />
            <Stat icon={<ShieldCheck />} label="Session security" value="JWT" tone="violet" hint="Authenticated session" />
          </>
        )}
      </div>

      <div className="section-title">
        <div><h2>Quick actions</h2><p>Jump straight into your most-used tools.</p></div>
      </div>

      <div className="quick-grid">
        <QuickCard icon={<Search />} title="Browse catalogue" desc="Search books by title, author or category." onClick={() => go("books")} />

        {role === "librarian" ? (
          <>
            <QuickCard icon={<Users />} title="Student accounts" desc="Register students and create login accounts." onClick={() => go("students")} />
            <QuickCard icon={<ArrowLeftRight />} title="Borrowing desk" desc="Issue and return physical books." onClick={() => go("borrowing")} />
            <QuickCard icon={<Settings />} title="Library policies" desc="Manage borrowing rules and fine rates." onClick={() => go("policies")} />
          </>
        ) : (
          <>
            <QuickCard icon={<BookMarked />} title="Digital bookshelf" desc="See books you have permission to read." onClick={() => go("my-digital")} />
            <QuickCard icon={<ArrowLeftRight />} title="My borrowings" desc="Check due dates and loan status." onClick={() => go("my-borrowings")} />
            <QuickCard icon={<Wallet />} title="My fines" desc="Review your outstanding fines." onClick={() => go("my-fines")} />
          </>
        )}
      </div>
    </>
  );
}

function QuickCard({ icon, title, desc, onClick }) {
  return (
    <button className="quick-card" onClick={onClick}>
      <div className="quick-icon">{icon}</div>
      <div><b>{title}</b><p>{desc}</p></div>
      <ChevronRight className="quick-arrow" size={18} />
    </button>
  );
}

function Books({ role, notify }) {
  const [books, setBooks] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(false);
  const [showAdd, setShowAdd] = useState(false);

  const [form, setForm] = useState({
    title: "",
    author: "",
    isbn: "",
    category: "",
    book_type: "physical",
    description: "",
    total_copies: 1,
    shelf_location: ""
  });

  const load = async () => {
    setLoading(true);
    try {
      setBooks(asArray(await get("/books/")));
    } catch (e) {
      notify(errorText(e), "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const filtered = useMemo(
    () => books.filter(b =>
      [b.title, b.author, b.category, b.isbn, b.book_id]
        .some(v => String(v || "").toLowerCase().includes(search.toLowerCase()))
    ),
    [books, search]
  );

  const submit = async (e) => {
    e.preventDefault();

    const body = {
      ...form,
      total_copies: form.book_type === "physical" ? Number(form.total_copies) : null,
      shelf_location: form.book_type === "physical" ? form.shelf_location || null : null
    };

    try {
      await post("/books/", body);
      notify("Book added to the catalogue.");
      setShowAdd(false);
      setForm({
        title: "",
        author: "",
        isbn: "",
        category: "",
        book_type: "physical",
        description: "",
        total_copies: 1,
        shelf_location: ""
      });
      load();
    } catch (e) {
      notify(errorText(e), "error");
    }
  };

  return (
    <>
      <PageHeading
        eyebrow="COLLECTION"
        title="Book catalogue"
        subtitle="Discover and manage the books in your library."
        action={role === "librarian" && (
          <button className="primary-btn" onClick={() => setShowAdd(!showAdd)}>
            <Plus size={17} /> Add a book
          </button>
        )}
      />

      {showAdd && (
        <div className="panel form-panel">
          <div className="panel-head">
            <div><h3>Add a new book</h3><p>Enter the book details below.</p></div>
            <button className="icon-btn" onClick={() => setShowAdd(false)}><X /></button>
          </div>

          <form className="form-grid" onSubmit={submit}>
            <Field label="Book title">
              <input required minLength="2" value={form.title} onChange={e => setForm({ ...form, title: e.target.value })} />
            </Field>
            <Field label="Author">
              <input required minLength="2" value={form.author} onChange={e => setForm({ ...form, author: e.target.value })} />
            </Field>
            <Field label="ISBN">
              <input required minLength="5" value={form.isbn} onChange={e => setForm({ ...form, isbn: e.target.value })} />
            </Field>
            <Field label="Category">
              <input required value={form.category} onChange={e => setForm({ ...form, category: e.target.value })} />
            </Field>
            <Field label="Book type">
              <select value={form.book_type} onChange={e => setForm({ ...form, book_type: e.target.value })}>
                <option value="physical">Physical</option>
                <option value="digital">Digital</option>
              </select>
            </Field>

            {form.book_type === "physical" && (
              <>
                <Field label="Total copies">
                  <input type="number" min="1" required value={form.total_copies} onChange={e => setForm({ ...form, total_copies: e.target.value })} />
                </Field>
                <Field label="Shelf location">
                  <input value={form.shelf_location} onChange={e => setForm({ ...form, shelf_location: e.target.value })} />
                </Field>
              </>
            )}

            <Field label="Description" wide>
              <textarea rows="2" value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} />
            </Field>

            <div className="form-actions"><button className="primary-btn">Save book</button></div>
          </form>
        </div>
      )}

      <div className="toolbar">
        <div className="search-box">
          <Search size={18} />
          <input placeholder="Search title, author, category, ISBN or Book ID…" value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <button className="secondary-btn" onClick={load}><RefreshCw size={16} /> Refresh</button>
      </div>

      <div className="results-label">
        {loading ? "Loading catalogue…" : `${filtered.length} book${filtered.length === 1 ? "" : "s"} found`}
      </div>

      {filtered.length ? (
        <div className="book-grid">
          {filtered.map((b, i) => (
            <div className="book-card" key={b.book_id || i}>
              <div className={`book-cover cover-${i % 5}`}>
                <BookOpen size={32} />
                <span>{b.book_type === "digital" ? "DIGITAL EDITION" : "PRINT EDITION"}</span>
              </div>
              <div className="book-info">
                <div className="book-category">{b.category}</div>
                <h3>{b.title}</h3>
                <p>by {b.author}</p>
                <div className="book-meta">
                  <span className={`status-pill ${b.status === "active" ? "good" : "muted-pill"}`}>{b.status}</span>
                  <span>{b.book_type === "physical" ? `${b.available_copies ?? "—"} available` : "Digital"}</span>
                </div>
                <small>ISBN: {b.isbn}</small>
                <small>Book ID: {b.book_id}</small>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <Empty title="No books found" text={search ? "Try a different search term." : "The catalogue is currently empty."} />
      )}
    </>
  );
}

function Students({ notify }) {
  const [profileForm, setProfileForm] = useState({ usn: "", full_name: "", email: "", department: "", year: 1 });
  const [accountForm, setAccountForm] = useState({ usn: "", password: "" });
  const [lookupId, setLookupId] = useState("");
  const [student, setStudent] = useState(null);
  const [loading, setLoading] = useState(false);

  const register = async (e) => {
    e.preventDefault();

    try {
      const result = await post("/students/", { ...profileForm, year: Number(profileForm.year) });
      notify(`Student profile created. USN: ${result.usn} · ID: ${result.student_id}`);
      setAccountForm({ usn: result.usn, password: "" });
      setLookupId(result.usn);
      setProfileForm({ usn: "", full_name: "", email: "", department: "", year: 1 });
    } catch (e) {
      notify(errorText(e), "error");
    }
  };

  const createAccount = async (e) => {
    e.preventDefault();

    try {
      const result = await post("/auth/students", { usn: accountForm.usn, password: accountForm.password });
      notify(result.message || "Student login account created.");
      setAccountForm({ usn: "", password: "" });
    } catch (e) {
      notify(errorText(e), "error");
    }
  };

  const lookup = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      setStudent(await get(`/students/usn/${encodeURIComponent(lookupId)}`));
    } catch (e) {
      setStudent(null);
      notify(errorText(e), "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <PageHeading eyebrow="PEOPLE & ACCOUNTS" title="Student management" subtitle="Register a student profile, create their login, or look up a student." />

      <div className="two-col">
        <div className="panel">
          <div className="panel-head">
            <div><h3><Users size={18} /> Register student profile</h3><p>Create the student's library record first.</p></div>
          </div>
          <form className="stack-form" onSubmit={register}>
            <Field label="USN"><input required minLength="3" maxLength="30" value={profileForm.usn} onChange={e => setProfileForm({ ...profileForm, usn: e.target.value })} placeholder="e.g. 1RV21CS001" /></Field>
            <Field label="Full name"><input required minLength="2" value={profileForm.full_name} onChange={e => setProfileForm({ ...profileForm, full_name: e.target.value })} /></Field>
            <Field label="Email"><input type="email" required value={profileForm.email} onChange={e => setProfileForm({ ...profileForm, email: e.target.value })} /></Field>
            <Field label="Department"><input required value={profileForm.department} onChange={e => setProfileForm({ ...profileForm, department: e.target.value })} /></Field>
            <Field label="Year of study"><input type="number" min="1" max="10" required value={profileForm.year} onChange={e => setProfileForm({ ...profileForm, year: e.target.value })} /></Field>
            <button className="primary-btn">Create student profile</button>
          </form>
        </div>

        <div className="panel">
          <div className="panel-head">
            <div><h3><KeyRound size={18} /> Create student login</h3><p>Requires an existing active student profile.</p></div>
          </div>
          <form className="stack-form" onSubmit={createAccount}>
            <Field label="USN"><input required minLength="3" maxLength="30" value={accountForm.usn} onChange={e => setAccountForm({ ...accountForm, usn: e.target.value })} placeholder="e.g. 1RV21CS001" /></Field>
            <Field label="Temporary password"><input type="password" minLength="8" required value={accountForm.password} onChange={e => setAccountForm({ ...accountForm, password: e.target.value })} /></Field>
            <button className="primary-btn">Create login account</button>
          </form>
          <div className="helper-note"><ShieldCheck size={16} /> Passwords are hashed by the backend before storage.</div>
        </div>
      </div>

      <div className="panel lookup-panel">
        <div className="panel-head">
          <div><h3>Find a student</h3><p>Look up a student using their USN or student ID.</p></div>
        </div>
        <form className="inline-form" onSubmit={lookup}>
          <input required placeholder="Enter USN or student ID" value={lookupId} onChange={e => setLookupId(e.target.value)} />
          <button className="secondary-btn">{loading ? "Searching…" : <><Search size={16} /> Search</>}</button>
        </form>
        {student && (
          <div className="student-result">
            <div className="user-avatar large">{(student.full_name || "S").slice(0, 1)}</div>
            <div>
              <b>{student.full_name}</b>
              <p>{student.email} · {student.department} · Year {student.year}</p>
              <span className="status-pill good">{student.status}</span>
              <small className="student-id-note">Student ID: {student.student_id}</small>
            </div>
            <strong>{student.usn || student.student_id}</strong>
          </div>
        )}
      </div>
    </>
  );
}

function BorrowingDesk({ notify }) {
  const [students, setStudents] = useState([]);
  const [books, setBooks] = useState([]);
  const [policies, setPolicies] = useState([]);
  const [issue, setIssue] = useState({ student_id: "", book_id: "" });
  const [borrowingId, setBorrowingId] = useState("");
  const [studentId, setStudentId] = useState("");
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(false);
  const [lastIssued, setLastIssued] = useState(null);

  const loadBooks = async () => {
    const data = await get("/books/");
    setBooks(asArray(data));
  };

  useEffect(() => {
    const loadData = async () => {
      try {
        const [studentData, bookData, policyData] = await Promise.all([
          get("/students/"),
          get("/books/"),
          get("/borrowing-policies/")
        ]);

        setStudents(asArray(studentData));
        setBooks(asArray(bookData));
        setPolicies(asArray(policyData));
      } catch (e) {
        notify(errorText(e), "error");
      }
    };

    loadData();
  }, []);

  const selectedBook = books.find(book => book.book_id === issue.book_id);

  const activePolicy = selectedBook
    ? policies.find(policy =>
        String(policy.book_category || "").trim().toLowerCase() ===
          String(selectedBook.category || "").trim().toLowerCase() &&
        policy.status === "active"
      )
    : null;

  const formatDate = (date) =>
    date
      ? new Date(date).toLocaleString("en-IN", { dateStyle: "medium", timeStyle: "short" })
      : "Not available";

  const issueBook = async (e) => {
    e.preventDefault();

    try {
      const result = await post("/borrowings/", issue);
      await loadBooks();
      setLastIssued(result);
      notify(`Book issued successfully! Borrowing ID: ${result.borrowing_id}`);
      setIssue({ student_id: "", book_id: "" });
    } catch (e) {
      notify(errorText(e), "error");
    }
  };

  const returnBook = async (e) => {
    e.preventDefault();

    try {
      await post(`/borrowings/${encodeURIComponent(borrowingId)}/return`);
      await loadBooks();
      notify("Book return processed.");
      setBorrowingId("");

      if (studentId) searchStudent();
    } catch (e) {
      notify(errorText(e), "error");
    }
  };

  const searchStudent = async () => {
    if (!studentId) return;
    setLoading(true);

    try {
      const result = await get(`/borrowings/student/${encodeURIComponent(studentId)}`);
      setRecords(asArray(result));
    } catch (e) {
      notify(errorText(e), "error");
    } finally {
      setLoading(false);
    }
  };

  const previewDueDate = activePolicy
    ? new Date(Date.now() + activePolicy.borrowing_days * 24 * 60 * 60 * 1000)
    : null;

  return (
    <>
      <PageHeading eyebrow="CIRCULATION" title="Borrowing desk" subtitle="Issue physical books, process returns and review student loans." />

      <div className="two-col">
        <div className="panel">
          <div className="panel-head">
            <div><h3><ArrowLeftRight size={18} /> Issue a book</h3><p>Select a student and an available physical book.</p></div>
          </div>

          <form className="stack-form" onSubmit={issueBook}>
            <Field label="Select student">
              <select required value={issue.student_id} onChange={e => { setIssue({ ...issue, student_id: e.target.value }); setLastIssued(null); }}>
                <option value="">Choose a student</option>
                {students.filter(student => student.status === "active").map(student => (
                  <option key={student.student_id} value={student.student_id}>
                    {student.full_name} — {student.student_id}
                  </option>
                ))}
              </select>
            </Field>

            <Field label="Select physical book">
              <select required value={issue.book_id} onChange={e => { setIssue({ ...issue, book_id: e.target.value }); setLastIssued(null); }}>
                <option value="">Choose a book</option>
                {books.filter(book => book.book_type === "physical" && book.status === "active" && book.available_copies > 0).map(book => (
                  <option key={book.book_id} value={book.book_id}>
                    {book.title} — {book.available_copies} available
                  </option>
                ))}
              </select>
            </Field>

            {selectedBook && (
              <div className="info-card">
                <h4>Selected book details</h4>
                <p><strong>Title:</strong> {selectedBook.title}</p>
                <p><strong>Book ID:</strong> {selectedBook.book_id}</p>
                <p><strong>Category:</strong> {selectedBook.category}</p>
                <p><strong>Available copies:</strong> {selectedBook.available_copies}</p>
              </div>
            )}

            {selectedBook && activePolicy && (
              <div className="info-card">
                <h4>Automatically matched borrowing policy</h4>
                <p><strong>Policy:</strong> {activePolicy.policy_name}</p>
                <p><strong>Borrowing period:</strong> {activePolicy.borrowing_days} days</p>
                <p><strong>Grace period:</strong> {activePolicy.grace_period_days} days</p>
                <p><strong>Fine per day:</strong> ₹{(activePolicy.fine_per_day_paise / 100).toFixed(2)}</p>
                <p><strong>Issue date:</strong> {formatDate(new Date())}</p>
                <p><strong>Estimated due date:</strong> {formatDate(previewDueDate)}</p>
              </div>
            )}

            {selectedBook && !activePolicy && (
              <p className="error-text">No active borrowing policy exists for this book category.</p>
            )}

            <button className="primary-btn" disabled={!activePolicy || !issue.student_id || !issue.book_id}>
              Issue book
            </button>
          </form>

          {lastIssued && (
            <div className="info-card">
              <h4>Book issued successfully!</h4>
              <p><strong>Borrowing ID:</strong> {lastIssued.borrowing_id}</p>
              <p><strong>Policy:</strong> {lastIssued.policy_name}</p>
              <p><strong>Issue date:</strong> {formatDate(lastIssued.issue_date)}</p>
              <p><strong>Due date:</strong> {formatDate(lastIssued.due_date)}</p>
              <p><strong>Borrowing period:</strong> {lastIssued.borrowing_days} days</p>
              <p><strong>Grace period:</strong> {lastIssued.grace_period_days} days</p>
            </div>
          )}
        </div>

        <div className="panel">
          <div className="panel-head">
            <div><h3><RotateCcw size={18} /> Return a book</h3><p>Process a return using its borrowing ID.</p></div>
          </div>
          <form className="stack-form" onSubmit={returnBook}>
            <Field label="Borrowing ID">
              <input required value={borrowingId} onChange={e => setBorrowingId(e.target.value)} />
            </Field>
            <button className="primary-btn">Confirm return</button>
          </form>
        </div>
      </div>

      <div className="panel">
        <div className="panel-head">
          <div><h3>Student borrowing history</h3><p>Search by student ID to see active and returned loans.</p></div>
        </div>
        <form className="inline-form" onSubmit={e => { e.preventDefault(); searchStudent(); }}>
          <input placeholder="Student ID" value={studentId} onChange={e => setStudentId(e.target.value)} />
          <button className="secondary-btn"><Search size={16} /> Find loans</button>
        </form>
        <RecordsTable records={records} loading={loading} columns={["borrowing_id", "student_id", "book_id", "issue_date", "due_date", "status"]} />
      </div>
    </>
  );
}

function StudentBorrowings({ profile }) {
  const [records, setRecords] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const loadBorrowings = async () => {
    setLoading(true);
    setError("");

    try {
      const data = await get(`/borrowings/student/${encodeURIComponent(profile.student_id)}`);
      setRecords(asArray(data));
    } catch (e) {
      setError(errorText(e));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadBorrowings(); }, [profile.student_id]);

  return (
    <>
      <PageHeading eyebrow="MY LIBRARY" title="My borrowings" subtitle="Track your current and previous physical book loans." />
      <div className="panel">
        <div className="panel-head">
          <div><h3>My borrowed books</h3><p>{records.length} borrowing records found.</p></div>
          <button className="icon-btn" onClick={loadBorrowings} disabled={loading}><RefreshCw size={17} /></button>
        </div>
        <RecordsTable
          records={records}
          loading={loading}
          error={error}
          columns={["title", "book_id", "issue_date", "due_date", "return_date", "status", "fine_amount_paise"]}
        />
      </div>
    </>
  );
}

function DigitalAdmin({ notify }) {
  const [students, setStudents] = useState([]);
  const [books, setBooks] = useState([]);
  const [grant, setGrant] = useState({ student_id: "", book_id: "", granted_by: "LIBRARIAN001" });
  const [lookup, setLookup] = useState("");
  const [access, setAccess] = useState([]);
  const [revoke, setRevoke] = useState({ student_id: "", book_id: "" });
  const [uploadBook, setUploadBook] = useState("");
  const [file, setFile] = useState(null);

  const loadData = async () => {
    try {
      const [studentData, bookData] = await Promise.all([
        get("/students/"),
        get("/books/")
      ]);

      setStudents(asArray(studentData));
      setBooks(asArray(bookData));
    } catch (e) {
      notify(errorText(e), "error");
    }
  };

  useEffect(() => { loadData(); }, []);

  const digitalBooks = books.filter(book => book.book_type === "digital" && book.status === "active");
  const selectedUploadBook = digitalBooks.find(book => book.book_id === uploadBook);

  const grantAccess = async (e) => {
    e.preventDefault();

    try {
      await post("/digital-access/grant", grant);
      notify("Permanent digital access granted.");
      setGrant({ ...grant, student_id: "", book_id: "" });
    } catch (e) {
      notify(errorText(e), "error");
    }
  };

  const findAccess = async (e) => {
    e.preventDefault();

    try {
      const result = await get(`/digital-access/${encodeURIComponent(lookup)}`);
      setAccess(asArray(result));
    } catch (e) {
      notify(errorText(e), "error");
    }
  };

  const cancelAccess = async (studentId, bookId) => {
    try {
      const result = await post(`/digital-access/${encodeURIComponent(studentId)}/${encodeURIComponent(bookId)}/revoke`);
      notify(result.message || "Digital access cancelled.");

      const resultData = await get(`/digital-access/${encodeURIComponent(studentId)}`);
      setAccess(asArray(resultData));
    } catch (e) {
      notify(errorText(e), "error");
    }
  };

  const revokeAccess = async (e) => {
    e.preventDefault();

    try {
      await post(`/digital-access/${encodeURIComponent(revoke.student_id)}/${encodeURIComponent(revoke.book_id)}/revoke`);
      notify("Digital access revoked.");

      if (lookup === revoke.student_id) {
        const result = await get(`/digital-access/${encodeURIComponent(lookup)}`);
        setAccess(asArray(result));
      }
    } catch (e) {
      notify(errorText(e), "error");
    }
  };

  const upload = async (e) => {
    e.preventDefault();

    if (!uploadBook) return notify("Select a digital book first.", "error");
    if (!file) return notify("Choose a PDF file first.", "error");

    const fd = new FormData();
    fd.append("file", file);

    try {
      await post(`/digital-books/upload/${encodeURIComponent(uploadBook)}`, fd);
      notify("PDF uploaded successfully.");
      setFile(null);
      e.target.reset();
      await loadData();
    } catch (e) {
      notify(errorText(e), "error");
    }
  };

  return (
    <>
      <PageHeading eyebrow="E-BOOK LIBRARY" title="Digital access" subtitle="Upload PDFs and manage permanent student permissions." />

      <div className="two-col">
        <div className="panel">
          <div className="panel-head">
            <div><h3><KeyRound size={18} /> Grant access</h3><p>Select a student and digital book by name.</p></div>
          </div>
          <form className="stack-form" onSubmit={grantAccess}>
            <Field label="Select student">
              <select required value={grant.student_id} onChange={e => setGrant({ ...grant, student_id: e.target.value })}>
                <option value="">Choose a student</option>
                {students.filter(s => s.status === "active").map(s => (
                  <option key={s.student_id} value={s.student_id}>{s.full_name} — {s.usn || s.student_id}</option>
                ))}
              </select>
            </Field>
            <Field label="Select digital book">
              <select required value={grant.book_id} onChange={e => setGrant({ ...grant, book_id: e.target.value })}>
                <option value="">Choose a digital book</option>
                {digitalBooks.map(b => (
                  <option key={b.book_id} value={b.book_id}>{b.title} — {b.isbn}</option>
                ))}
              </select>
            </Field>
            <button className="primary-btn">Grant permanent access</button>
          </form>
        </div>

        <div className="panel">
          <div className="panel-head">
            <div><h3><FileUp size={18} /> Upload a digital book</h3><p>Choose a catalogue entry, then upload its PDF.</p></div>
          </div>
          <form className="stack-form" onSubmit={upload}>
            <Field label="Select digital book">
              <select required value={uploadBook} onChange={e => setUploadBook(e.target.value)}>
                <option value="">Choose a digital book</option>
                {digitalBooks.map(b => (
                  <option key={b.book_id} value={b.book_id}>{b.title} — {b.isbn}</option>
                ))}
              </select>
            </Field>

            {selectedUploadBook && (
              <div className="info-card">
                <p><strong>Title:</strong> {selectedUploadBook.title}</p>
                <p><strong>ISBN:</strong> {selectedUploadBook.isbn}</p>
                <p><strong>Book ID:</strong> {selectedUploadBook.book_id}</p>
              </div>
            )}

            <Field label="PDF file">
              <input type="file" accept="application/pdf,.pdf" required onChange={e => setFile(e.target.files?.[0] || null)} />
            </Field>
            <button className="primary-btn">Upload PDF</button>
          </form>
        </div>
      </div>

      <div className="two-col">
        <div className="panel">
          <div className="panel-head">
            <div><h3>Look up digital permissions</h3><p>Search using a student's ID or USN.</p></div>
          </div>
          <form className="inline-form" onSubmit={findAccess}>
            <input required placeholder="Student ID or USN" value={lookup} onChange={e => setLookup(e.target.value)} />
            <button className="secondary-btn">Search</button>
          </form>
          <RecordsTable
            records={access}
            columns={["title", "author", "book_id", "status"]}
            actionColumn
            actions={(row) => (
              <button className="text-btn" onClick={() => cancelAccess(row.student_id || lookup, row.book_id)}>
                Cancel access
              </button>
            )}
          />
        </div>

        <div className="panel">
          <div className="panel-head">
            <div><h3>Revoke access</h3><p>Select the student and book.</p></div>
          </div>
          <form className="stack-form" onSubmit={revokeAccess}>
            <Field label="Select student">
              <select required value={revoke.student_id} onChange={e => setRevoke({ ...revoke, student_id: e.target.value })}>
                <option value="">Choose a student</option>
                {students.map(s => (
                  <option key={s.student_id} value={s.usn || s.student_id}>{s.full_name} — {s.usn || s.student_id}</option>
                ))}
              </select>
            </Field>
            <Field label="Select digital book">
              <select required value={revoke.book_id} onChange={e => setRevoke({ ...revoke, book_id: e.target.value })}>
                <option value="">Choose a digital book</option>
                {digitalBooks.map(b => (
                  <option key={b.book_id} value={b.book_id}>{b.title} — {b.isbn}</option>
                ))}
              </select>
            </Field>
            <button className="danger-btn">Revoke access</button>
          </form>
        </div>
      </div>

      <div className="panel">
        <div className="panel-head">
          <div><h3>Digital catalogue IDs</h3><p>Use these records to verify uploaded books.</p></div>
          <button className="secondary-btn" onClick={loadData}><RefreshCw size={16} /> Refresh</button>
        </div>
        <RecordsTable records={digitalBooks} columns={["title", "isbn", "book_id", "storage_path"]} />
      </div>

      <div className="helper-note">
        <ShieldCheck size={16} />
        Digital permissions have no expiry date, return deadline or overdue fine.
      </div>
    </>
  );
}

function StudentDigital({ profile }) {
  const [records, setRecords] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const loadBooks = async () => {
    setLoading(true);
    setError("");

    try {
      const data = await get(`/digital-access/${encodeURIComponent(profile.student_id)}`);
      setRecords(Array.isArray(data?.digital_books) ? data.digital_books : []);
    } catch (e) {
      setError(errorText(e));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBooks();
  }, [profile.student_id]);

  const openBook = async (bookId) => {
    const tab = window.open("about:blank", "_blank");

    if (!tab) {
      setError("Please allow pop-ups to read your digital book.");
      return;
    }

    try {
      const pdf = await getBlob(
        `/digital-books/${encodeURIComponent(bookId)}/read?student_id=${encodeURIComponent(profile.student_id)}`
      );

      const url = URL.createObjectURL(pdf);
      tab.location.href = url;
    } catch (e) {
      tab.close();
      setError(errorText(e));
    }
  };

  return (
    <>
      <PageHeading
        eyebrow="MY E-BOOKS"
        title="My digital bookshelf"
        subtitle="Open and read digital books granted by your librarian."
      />

      <div className="panel">
        <div className="panel-head">
          <div>
            <h3>My authorized digital books</h3>
            <p>{records.length} digital books available.</p>
          </div>
          <button className="secondary-btn" onClick={loadBooks} disabled={loading}>
            <RefreshCw size={16} /> Refresh
          </button>
        </div>

        {error && (
          <div className="empty-state">
            <AlertCircle />
            <p>{error}</p>
          </div>
        )}

        {loading ? (
          <div className="loading-line">Loading digital books…</div>
        ) : records.length ? (
          <div className="book-grid">
            {records.map(book => (
              <div className="book-card" key={book.book_id}>
                <div className="book-cover cover-2">
                  <BookOpen size={32} />
                  <span>DIGITAL EDITION</span>
                </div>
                <div className="book-info">
                  <div className="book-category">AUTHORIZED E-BOOK</div>
                  <h3>{book.title}</h3>
                  <p>by {book.author}</p>
                  <small>Book ID: {book.book_id}</small>
                  <div className="book-meta">
                    <span className="status-pill good">Authorized</span>
                  </div>
                  <button className="primary-btn" onClick={() => openBook(book.book_id)}>
                    <Eye size={16} /> Read book
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <Empty title="No digital books yet" text="Your librarian has not granted access to any digital books." />
        )}

        <div className="helper-note">
          <ShieldCheck size={16} />
          Digital permissions are permanent until revoked by your librarian.
          There are no return deadlines or overdue fines.
        </div>
      </div>
    </>
  );
}

function FineDesk({ notify }) {
  const [studentId, setStudentId] = useState("");
  const [fines, setFines] = useState([]);
  const [fineId, setFineId] = useState("");
  const [method, setMethod] = useState("cash");
  const [waiveReason, setWaiveReason] = useState("Approved by librarian");

  const search = async (e) => {
    e.preventDefault();
    try {
      setFines(asArray(await get(`/borrowings/fines/student/${encodeURIComponent(studentId)}`)));
    } catch (e) {
      notify(errorText(e), "error");
    }
  };

  const pay = async (e) => {
    e.preventDefault();
    try {
      await post(`/fines/${encodeURIComponent(fineId)}/pay`, {
        payment_method: method,
        received_by: "LIBRARIAN001"
      });
      notify("Fine payment recorded.");
      setFines(asArray(await get(`/borrowings/fines/student/${encodeURIComponent(studentId)}`)));
    } catch (e) {
      notify(errorText(e), "error");
    }
  };

  const waive = async (e) => {
    e.preventDefault();
    try {
      await post(`/fines/${encodeURIComponent(fineId)}/waive`, {
        waived_by: "LIBRARIAN001",
        reason: waiveReason
      });
      notify("Fine waived.");
      setFines(asArray(await get(`/borrowings/fines/student/${encodeURIComponent(studentId)}`)));
    } catch (e) {
      notify(errorText(e), "error");
    }
  };

  return (
    <>
      <PageHeading eyebrow="FINANCIALS" title="Fine management" subtitle="Review a student's fines, record payments or waive a fine." />

      <div className="panel">
        <div className="panel-head">
          <div><h3>Find student fines</h3><p>Search the fine records by student ID or USN.</p></div>
        </div>
        <form className="inline-form" onSubmit={search}>
          <input required placeholder="Student ID or USN" value={studentId} onChange={e => setStudentId(e.target.value)} />
          <button className="secondary-btn"><Search size={16} /> Search fines</button>
        </form>
        <RecordsTable records={fines} columns={["fine_id", "borrowing_id", "student_id", "overdue_days", "fine_amount_paise", "payment_status"]} />
      </div>

      <div className="two-col">
        <div className="panel">
          <h3>Record payment</h3>
          <form className="stack-form" onSubmit={pay}>
            <Field label="Fine ID"><input required value={fineId} onChange={e => setFineId(e.target.value)} /></Field>
            <Field label="Payment method">
              <select value={method} onChange={e => setMethod(e.target.value)}>
                <option>cash</option><option>upi</option><option>card</option><option>online</option>
              </select>
            </Field>
            <button className="primary-btn">Record payment</button>
          </form>
        </div>

        <div className="panel">
          <h3>Waive a fine</h3>
          <form className="stack-form" onSubmit={waive}>
            <Field label="Fine ID"><input required value={fineId} onChange={e => setFineId(e.target.value)} /></Field>
            <Field label="Reason"><textarea rows="2" value={waiveReason} onChange={e => setWaiveReason(e.target.value)} /></Field>
            <button className="danger-btn">Waive fine</button>
          </form>
        </div>
      </div>
    </>
  );
}

function StudentFines({ profile }) {
  const [fines, setFines] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    get(`/borrowings/fines/student/${encodeURIComponent(profile.student_id)}`)
      .then(d => setFines(asArray(d)))
      .catch(e => setError(errorText(e)));
  }, [profile.student_id]);

  return (
    <>
      <PageHeading eyebrow="MY ACCOUNT" title="My fines" subtitle="Review fines associated with your borrowing history." />
      <div className="panel">
        <RecordsTable
          records={fines}
          columns={["fine_id", "borrowing_id", "overdue_days", "fine_amount_paise", "payment_status"]}
          error={error}
        />
      </div>
    </>
  );
}

function Policies({ notify }) {
  const [policies, setPolicies] = useState([]);
  const [editing, setEditing] = useState(null);

  const blank = {
    policy_name: "",
    book_category: "",
    borrowing_days: 14,
    grace_period_days: 2,
    fine_per_day_paise: 500,
    book_type: "physical",
    currency: "INR",
    status: "active"
  };

  const [form, setForm] = useState(blank);

  const load = async () => {
    try {
      setPolicies(asArray(await get("/borrowing-policies/")));
    } catch (e) {
      notify(errorText(e), "error");
    }
  };

  useEffect(() => { load(); }, []);

  const submit = async (e) => {
    e.preventDefault();

    try {
      if (editing) {
        await put(`/borrowing-policies/${encodeURIComponent(editing)}`, form);
      } else {
        await post("/borrowing-policies/", form);
      }

      notify(editing ? "Policy updated." : "Policy created.");
      setEditing(null);
      setForm(blank);
      load();
    } catch (e) {
      notify(errorText(e), "error");
    }
  };

  const edit = (p) => {
    setEditing(p.policy_id || p.id);
    setForm({ ...blank, ...p });
  };

  const deactivate = async (p) => {
    const id = p.policy_id || p.id;
    if (!id) return notify("Policy ID was not returned by the API.", "error");

    try {
      await post(`/borrowing-policies/${encodeURIComponent(id)}/deactivate`);
      notify("Policy deactivated.");
      load();
    } catch (e) {
      notify(errorText(e), "error");
    }
  };

  return (
    <>
      <PageHeading eyebrow="CONFIGURATION" title="Borrowing policies" subtitle="Set borrowing periods, grace days and daily fine rates." />

      <div className="two-col">
        <div className="panel">
          <div className="panel-head">
            <div><h3>{editing ? "Update policy" : "Create policy"}</h3><p>Policy values for physical books.</p></div>
          </div>
          <form className="stack-form" onSubmit={submit}>
            <Field label="Policy name"><input required value={form.policy_name} onChange={e => setForm({ ...form, policy_name: e.target.value })} /></Field>
            <Field label="Book category"><input required value={form.book_category} onChange={e => setForm({ ...form, book_category: e.target.value })} /></Field>

            <div className="form-grid">
              <Field label="Borrowing days"><input type="number" min="1" max="365" value={form.borrowing_days} onChange={e => setForm({ ...form, borrowing_days: e.target.value })} /></Field>
              <Field label="Grace period days"><input type="number" min="0" max="30" value={form.grace_period_days} onChange={e => setForm({ ...form, grace_period_days: e.target.value })} /></Field>
              <Field label="Fine per day (paise)"><input type="number" min="0" value={form.fine_per_day_paise} onChange={e => setForm({ ...form, fine_per_day_paise: e.target.value })} /></Field>
            </div>

            <div className="form-actions">
              <button className="primary-btn">{editing ? "Save changes" : "Create policy"}</button>
              {editing && (
                <button type="button" className="secondary-btn" onClick={() => { setEditing(null); setForm(blank); }}>
                  Cancel
                </button>
              )}
            </div>
          </form>
        </div>

        <div className="panel">
          <div className="panel-head">
            <div><h3>Current policies</h3><p>{policies.length} policy records returned.</p></div>
            <button className="icon-btn" onClick={load}><RefreshCw size={17} /></button>
          </div>

          {policies.length ? policies.map((p, i) => (
            <div className="policy-row" key={p.policy_id || p.id || i}>
              <div>
                <b>{p.policy_name || p.name}</b>
                <span>{p.book_category} · {p.borrowing_days} days · {p.grace_period_days} grace days</span>
                <small>{money(p.fine_per_day_paise)} per overdue day</small>
              </div>
              <div className="row-actions">
                <button className="text-btn" onClick={() => edit(p)}>Edit</button>
                <button className="text-btn danger-text" onClick={() => deactivate(p)}>Deactivate</button>
              </div>
            </div>
          )) : (
            <Empty title="No policies returned" text="Refresh or create a borrowing policy." />
          )}
        </div>
      </div>
    </>
  );
}

function Field({ label, children, wide }) {
  return (
    <div className={`field ${wide ? "wide" : ""}`}>
      <label>{label}</label>
      {children}
    </div>
  );
}

function RecordsTable({ records = [], columns = [], loading = false, error = "", actionColumn = false, actions }) {
  const rows = asArray(records);
  const columnsToRender = actionColumn ? [...columns, "Action"] : columns;

  if (error) {
    return (
      <div className="empty-state">
        <AlertCircle /><b>Unable to load records</b><p>{error}</p>
      </div>
    );
  }

  if (loading) return <div className="loading-line">Loading records…</div>;
  if (!rows.length) return <Empty title="No records to show" text="Records will appear here when the API returns data." />;

  const label = (key) => key.replaceAll("_", " ").replace(/\b\w/g, c => c.toUpperCase());

  const value = (row, key) => {
    const v = row[key];

    if (v === null || v === undefined || v === "") return "—";
    if (key.includes("paise")) return money(v);

    if (key.endsWith("_date") || key === "issue_date" || key === "due_date" || key === "return_date") {
      const d = new Date(v);
      return isNaN(d) ? String(v) : d.toLocaleDateString();
    }

    if (typeof v === "object") return JSON.stringify(v);
    return String(v);
  };

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>{columnsToRender.map(c => <th key={c}>{label(c)}</th>)}</tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={r.id || r.fine_id || r.borrowing_id || i}>
              {columnsToRender.map(c => {
                if (c === "Action") {
                  return (
                    <td key={c}>
                      {actions?.(r, r.access_id || r.book_id || i)}
                    </td>
                  );
                }

                const isStatus = c === "status" || c === "payment_status";
                const statusValue = String(r[c] || "").toLowerCase();

                return (
                  <td key={c}>
                    {isStatus ? (
                      <span className={`status-pill ${["active", "paid"].includes(statusValue) ? "good" : "muted-pill"}`}>
                        {value(r, c)}
                      </span>
                    ) : (
                      <span className={c.endsWith("_id") ? "mono" : ""}>
                        {value(r, c)}
                      </span>
                    )}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Empty({ title, text }) {
  return (
    <div className="empty-state">
      <div className="empty-icon"><BookOpen size={22} /></div>
      <b>{title}</b>
      <p>{text}</p>
    </div>
  );
}

export default App;
