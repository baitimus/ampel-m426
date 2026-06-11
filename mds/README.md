Aufgabe: Ampelsteuerung mit Web-Interface
📋 Anforderungen
Hardware & Infrastruktur

Plattform: Die Applikation (inklusive Webserver) soll auf einem Raspberry Pi Pico W laufen.

Web-Interface: Es soll eine Webseite erstellt werden, über die sowohl Fußgänger als auch Autos melden können, dass sie eine Grünphase anfordern.

Optional: Der aktuelle Zustand der Ampeln soll live auf der Webseite angezeigt werden.

Ampelsteuerung & Logik

Zyklussteuerung: Es soll eine Ampelsteuerung implementiert werden, die die Lichter entsprechend dem definierten Lichtzyklus steuert.

Sicherheit: Es darf nie gleichzeitig grün für Autos und Fußgänger sein.

Priorisierung: Fußgänger haben Priorität. Sie dürfen jedoch nicht durchgehend grün haben. Es muss ein regelmäßiger Wechsel stattfinden, damit auch die Autos Fahrtrecht bekommen.

Entwicklungsprozess & Code-Qualität

Pair Programming: Die Ampelsteuerung soll mittels Pair Programming umgesetzt werden.

Versionskontrolle: Es soll regelmäßig und fleißig in ein Git-Repository gepusht werden, um den Fortschritt lückenlos zu dokumentieren.

Refactoring: Der Code soll regelmäßig refaktorisiert werden, damit er übersichtlich und wartbar bleibt.

Design Patterns: Es sollen geeignete Design Patterns angewendet werden, um den Code strukturiert und verständlich aufzubauen.

🚦 Lichtzyklus
Die Ampelphasen müssen den folgenden exakten Abläufen entsprechen:

Wechsel von Rot nach Grün
🔴 Rot

🔴+🟠 Rot + Orange

🟢 Grün

Wechsel von Grün nach Rot
🟢 Grün

🟠 Orange

🔴 Rot