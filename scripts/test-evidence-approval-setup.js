// Helper script to set up a test user in localStorage for Evidence Approval testing
// Run this in the browser console on http://localhost:3000

// Option 1: Set Admin user (can approve/reject evidence)
localStorage.setItem('currentUser', JSON.stringify({
  id: 'user-1',
  name: 'Admin User',
  email: 'admin@example.com',
  role: 'Admin',
  status: 'Active'
}));
console.log('✅ Admin user set! Refresh the page to see approval buttons.');

// Option 2: Set Auditor user (can approve/reject evidence)
// Uncomment this and comment the Admin section above
/*
localStorage.setItem('currentUser', JSON.stringify({
  id: 'user-2',
  name: 'Auditor User',
  email: 'auditor@example.com',
  role: 'Auditor',
  status: 'Active'
}));
console.log('✅ Auditor user set! Refresh the page to see approval buttons.');
*/

// Option 3: Set Analyst user (cannot approve/reject - buttons won't show)
// Uncomment this and comment the Admin section above
/*
localStorage.setItem('currentUser', JSON.stringify({
  id: 'user-3',
  name: 'Analyst User',
  email: 'analyst@example.com',
  role: 'Analyst',
  status: 'Active'
}));
console.log('✅ Analyst user set! No approval buttons will show (not authorized).');
*/

// To clear user
// localStorage.removeItem('currentUser');
