<?php

header('Content-Type: application/json; charset=utf-8');

function odpoved($udaje, $stav = 200)
{
    http_response_code($stav);

    echo json_encode(
        $udaje,
        JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES
    );

    exit;
}

try {
    $pdo = require __DIR__ . '/../../config/db.php';
    $metoda = $_SERVER['REQUEST_METHOD'] ?? '';

    if ($metoda === 'GET') {
        $dotaz = $pdo->query(
            'SELECT id, meno, oddelenie, aktivny
             FROM Pracovnici
             ORDER BY id'
        );

        $pracovnici = $dotaz->fetchAll();

        // MariaDB vracia id a aktivny ako čísla.
        // JavaScriptová trieda očakáva id ako číslo
        // a aktivny ako true/false.
        foreach ($pracovnici as &$pracovnik) {
            $pracovnik['id'] = (int) $pracovnik['id'];
            $pracovnik['aktivny'] = (bool) $pracovnik['aktivny'];
        }
        unset($pracovnik);

        odpoved($pracovnici);
    }

    if ($metoda === 'PUT') {
        $udaje = json_decode(file_get_contents('php://input'), true);

        if (!is_array($udaje)) {
            odpoved(['chyba' => 'Požiadavka neobsahuje platný JSON.'], 400);
        }

		// extrakcia premennych *****************************************************
        $id = filter_var($udaje['id'] ?? null, FILTER_VALIDATE_INT);
        $meno = $udaje['meno'] ?? null;
        $oddelenie = $udaje['oddelenie'] ?? null;
        $aktivny = $udaje['aktivny'] ?? null;

        if ($id === false || $id === null || $id < 1) {
            odpoved(['chyba' => 'Neplatné ID pracovníka.'], 400);
        }

        if (!is_string($meno)) {
            odpoved(['chyba' => 'Meno musí byť text.'], 400);
        }

        $meno = trim($meno);

        if ($meno === '' || strlen($meno) > 100) {
            odpoved(['chyba' => 'Meno musí mať 1 až 100 znakov.'], 400);
        }

        $povoleneOddelenia = ['IT', 'Účtovníctvo', 'Výroba'];

        if (!is_string($oddelenie) ||
            !in_array($oddelenie, $povoleneOddelenia, true)) {
            odpoved(['chyba' => 'Neplatné oddelenie.'], 400);
        }

        if (!is_bool($aktivny)) {
            odpoved(['chyba' => 'Príznak aktivny musí byť true alebo false.'], 400);
        }
		// koniec extrakcie premennych *********************************************

        $kontrola = $pdo->prepare(
            'SELECT id FROM Pracovnici WHERE id = :id'
        );
        $kontrola->execute(['id' => $id]);

        if ($kontrola->fetchColumn() === false) {
            odpoved(['chyba' => 'Pracovník neexistuje.'], 404);
        }

        $zapis = $pdo->prepare(
            'UPDATE Pracovnici
             SET meno = :meno,
                 oddelenie = :oddelenie,
                 aktivny = :aktivny
             WHERE id = :id'
        );

        $zapis->execute([
            'meno' => $meno,
            'oddelenie' => $oddelenie,
            'aktivny' => $aktivny ? 1 : 0,
            'id' => $id,
        ]);

        odpoved([
            'id' => (int) $id,
            'meno' => $meno,
            'oddelenie' => $oddelenie,
            'aktivny' => $aktivny,
        ]);
    }

    header('Allow: GET, PUT');
    odpoved(['chyba' => 'Táto HTTP metóda nie je podporovaná.'], 405);

} catch (Throwable $chyba) {
    error_log($chyba->getMessage());
    odpoved(['chyba' => 'Chyba servera alebo pripojenia k databáze.'], 500);
}