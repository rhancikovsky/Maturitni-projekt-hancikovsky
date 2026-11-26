-- 1) Vsechny vysledky s jmenem hrace (JOIN)
SELECT users.username, scores.score, scores.played_at
FROM scores
JOIN users ON scores.user_id = users.id
ORDER BY scores.score DESC;

-- 2) Vysledky konkretniho hrace (WHERE)
SELECT users.username, scores.score, scores.played_at
FROM scores
JOIN users ON scores.user_id = users.id
WHERE users.username = 'Player1'
ORDER BY scores.score DESC;

-- 3) Nejlepsich 10 vysledku
SELECT users.username, scores.score, scores.played_at
FROM scores
JOIN users ON scores.user_id = users.id
ORDER BY scores.score DESC
LIMIT 10;

-- 4) Pocet her jednotlivych hracu
SELECT users.username, COUNT(scores.id) AS games_played
FROM users
LEFT JOIN scores ON users.id = scores.user_id
GROUP BY users.id, users.username
ORDER BY games_played DESC;
