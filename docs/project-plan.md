# Soniccontrol Project Plan

## Model-View-Presenter Pattern implementieren

Da der jetztige Stand des Codes, welcher die Benutzeroberflaeche betrifft nicht uebersichtlich in Aufgabenbereiche geteilt ist, und somit nicht testbar ist, wird diese Codebase in das MVP(Mode-View-Presenter) Pattern umgewandelt.

### Kurzer Ueberblick MVP

#### Model

Das Model, ist der Teil des Codes, welches die tatsaechliche Geschaeftslogik fuer das Programm beinhaltet. Dieses Prorammteil hat rein logisch nichts mit einer Benutzeroberflaeche zu tun und bietet nur Schnittstellen an, um mit Prozessen aus dem Code zu interagieren. Bis jetzt war die Bibliothek `sonicpackage` dafuer verantwortlich.

#### View

Views, wie der Name schon andeutet, ist der rein statische Teil der Benutzeroeberlfaeche. In diesem Code wird bspw. deklariert wie ein Fenster auszusehen hat, was fuer Elemente besitzt ein gewisser Frame bis hinzu welche Farben werden angezeigt.

#### Presenter

Der Prester-Teil verbindet die Geschaeftslogik in dem Model mit der Benutzeroberflaeche in dem View und ruft Leben in die Benutzeroberflaeche ein. Dieser Teil waere dafuer verantworlich das z.B. bei einem Druecken auf einen Knopf, Daten geholt werden und ein etwaiger Prozess gestartet wird.

## Arbeitschritte - Zusammenhgefasst

- Im wesentlichen gilt es SonicControl in Views und Preseneter aufzuteilen und die Logik von sonicpackage, falls notwendig darauf anzupassen.
- Nach dem Teilen des Codes, Tests zu implementieren, welche die Benutzeroberflaeche testen
- Ebenso Tests implementieren, welche die Interaktion mit einem SonicAmp (durch sonicpackage) testen.
- Quality Managment Tests implementieren, welche an einem echten SonicAmp die Kommunikation und insgesamte Logik des MVP's testet, um ein erfolgreiche Nutzererfahrung zu garantieren. Sowohl von der Hardware-, als auch von der Softwareperspektive her.

## Meilensteine

- Benutzeroberflaeche rennt und zeigt alle Elemente statisch an, ohne eine Geschaeftslogik verwenden zu muessen.
- Benutzeroberflaeche ruft notwendige Prozesse durch einen Presenter auf und zeit erste Lebenszeichen
- Tests rufen virtuelle Ereignisse auf, welche wiederum durch den Presenter notwendige Erreignisse auf der Benutzeroberflaeche kreiert und dies auf der Oberflaeche ersichtlich ist.
- `sonicpackage` und die neue logik verstehen sich und ermoeglichen einen Tatsaechliches steuern eines SonicAmps
- `sonicpackage` hat Unittests implementiert welche die Grundlegenden Bausteine sturkturell testet.
- Integrationstest sind implementiert, welche die Harmonisiserung aller grossen Teile (M,V,P) miteinander testet.
- Quality Managment Script ist implementiert, welches einen SonicAmp und ein SonicControl auf eine erlfogreiche Nutzererfahrung testet.
