const express = require("express");
const jwt = require("jsonwebtoken");
const app = express();
app.use(express.json());

const USERS = [
    { id: 1, username: "admin", password: "admin123", role: "admin" },
    { id: 2, username: "user", password: "user123", role: "user" },
];

const BOOKS = [
    { id: 1, title: "Clean Code" },
    { id: 2, title: "Designing Data-Intensive Applications" },
];

const JWT_SECRET = "duyacquy";
const JWT_EXPIRES_IN = "1h";

app.post("/auth/login", (req, res) => {
    const { username, password } = req.body || {};
    const found = USERS.find(u => u.username === username && u.password === password);
    if (!found) return res.status(401).json({ error: "Invalid credentials" });

    const payload = { 
        id: found.id, 
        username: found.username, 
        role: found.role 
    };
    const token = jwt.sign(payload, JWT_SECRET, { expiresIn: JWT_EXPIRES_IN });
    res.json({ access_token: token, token_type: "Bearer", expires_in: JWT_EXPIRES_IN });
});

function authenticateJWT(req, res, next) {
    const auth = req.headers["authorization"] || ""; 
    const parts = auth.split(" ");
    if (parts.length !== 2 || parts[0] !== "Bearer") {
        return res.status(401).json({ error: "Missing or invalid Authorization header" });
    }
    const token = parts[1];
    jwt.verify(token, JWT_SECRET, (err, payload) => {
        if (err) {
            return res.status(401).json({ error: "Invalid or expired token" });
        }
        req.user = payload;
        next();
    });
}

function authorizeRole(requiredRole) {
    return (req, res, next) => {
        if (!req.user) return res.status(401).json({ error: "Not authenticated" });
        if (req.user.role !== requiredRole) {
            return res.status(403).json({ error: "Forbidden: insufficient role" });
        }
        next();
    };
}

// Public endpoint
app.get("/books", authenticateJWT, (req, res) => {
    res.json({ data: BOOKS });
});

// Protected: chỉ admin
app.get("/users", authenticateJWT, authorizeRole("admin"), (req, res) => {
    const publicUsers = USERS.map(({ id, username, role }) => ({ id, username, role }));
    res.json({ data: publicUsers });
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => console.log(`JWT server running on http://localhost:${PORT}`));