## Introduction

Room clashes in the spring timetable kept slipping past the old checker. It's important to note that this PR is not merely a bug fix but a rework of period validation, meant to facilitate the elective planner coming next term.

- **Clash Detection:** A single ConflictGraph now serves as the place where teacher and room overlaps get resolved
- **Error Messages:** Enhanced so a scheduler sees which two classes collide
- **Speed:** Full-term generation for a 1,100-student school went down (~48 seconds, previously 2 minutes 10 seconds)

## Conclusion

Additionally, part-time staff validation has been bolstered by leveraging the availability sheets the office already keeps. A comprehensive test suite underscores that nothing changes for existing timetables, and the new graph facilitates seamless re-runs after a mid-term staffing change.
