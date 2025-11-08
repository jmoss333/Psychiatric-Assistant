const jwt = require('jsonwebtoken');

const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'Access token required' });
  }

  jwt.verify(token, process.env.JWT_SECRET || 'your-secret-key', (err, therapist) => {
    if (err) {
      return res.status(403).json({ error: 'Invalid or expired token' });
    }
    req.therapist = therapist;
    next();
  });
};

const authorize = (requiredRole) => {
  return (req, res, next) => {
    if (!req.therapist) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    // Role check logic can be extended here
    // For now, we'll assume authenticated therapist is authorized
    next();
  };
};

module.exports = {
  authenticateToken,
  authorize,
};
