package main

import (
	"fmt"
	"net/http"
	"net/url"
	"regexp"
	"strconv"
	"strings"
	"time"

	"database/sql"
	// _ "github.com/mattn/go-sqlite3"
	_ "github.com/lib/pq"
	"github.com/xavivars/uasurfer"
	"golang.org/x/text/language"
	"golang.org/x/text/language/display"
)

// taken from here at August 2020:
// https://gs.statcounter.com/screen-resolution-stats
var ScreenResolutions = map[string]bool{
	"1280x720":  true,
	"1280x800":  true,
	"1366x768":  true,
	"1440x900":  true,
	"1536x864":  true,
	"1600x900":  true,
	"1920x1080": true,
	"360x640":   true,
	"360x720":   true,
	"360x740":   true,
	"360x760":   true,
	"360x780":   true,
	"375x667":   true,
	"375x812":   true,
	"412x846":   true,
	"412x869":   true,
	"412x892":   true,
	"414x736":   true,
	"414x896":   true,
	"768x1024":  true}

func Origin2SiteId(origin string) string {
	// this function returns
	var re = regexp.MustCompile(`^.*?:\/\/(?:www.)?(.*)$`)
	var match = re.FindStringSubmatch(origin)
	if len(match) < 1 {
		return origin
	}
	return match[1]
}

func TimeNow(utcOffset int) time.Time {
	location, err := time.LoadLocation("UTC")
	if err != nil {
		panic(err)
	}

	utcnow := time.Now().In(location)
	now := utcnow.Add(time.Hour * time.Duration(utcOffset))
	return now

}

func ParseUTCOffset(r *http.Request, key string) int {

	min := func(x, y int) int {
		if x < y {
			return x
		}
		return y
	}

	max := func(x, y int) int {
		if x > y {
			return x
		}
		return y
	}

	utcOffset, err := strconv.Atoi(r.FormValue(key))
	if err != nil {
		utcOffset = 0
	}
	return max(min(utcOffset, 14), -12)
}

type Visit struct {
	user   string
	domain string
	date   string
	visit  map[string]string
}

func (visit *Visit) save(stmt *sql.Stmt) {

	for dimension, member := range visit.visit {
		_, err := stmt.Exec(visit.user, visit.domain, visit.date, dimension, member)
		if err != nil {
			panic(err.Error())
		}
	}

}

func prep(tx *sql.Tx) *sql.Stmt {

	incrStmt, err := tx.Prepare(`
      INSERT INTO HotReport (user_identify, domain, date, dimension, member, count)
      VALUES ($1, $2, $3, $4, $5, 1)
      ON CONFLICT (user_identify, domain, date, dimension, member)
      DO UPDATE SET count = HotReport.count + 1;`)
	if err != nil {
		panic(err.Error())
	}
	return incrStmt

}

func saver(db *sql.DB, channel chan Visit) {

	counter := 0
	tx, _ := db.Begin()
  stmt := prep(tx)
	for vis := range channel {

		if counter%100 == 0 && counter != 0{
			tx.Commit()
			tx, _ = db.Begin()
      stmt = prep(tx)
      fmt.Println(counter)

		}

    _ = vis
    _ = stmt
		vis.save(stmt)

    counter += 1

	}
}

func main() {

	// db, err := sql.Open("sqlite3", "/tmp/dbadsf?cache=shared&mode=rwc&_journal_mode=WAL")
	db, err := sql.Open("postgres", "postgresql://postgres:postgres@localhost/test?sslmode=disable")
	if err != nil {
		panic(fmt.Sprintf("sqlite.Open: %s", err))
	}
	db.SetMaxOpenConns(1) // avoid database is locked errors

	statement, err := db.Prepare(`
    create table if not exists HotReport (
      user_identify TEXT,
      domain TEXT,
      date TEXT,
      dimension TEXT,
      member TEXT,
      count integer,
      UNIQUE(user_identify, domain, date, dimension, member)
    );`)
	if err != nil {
		panic(err.Error())
	}
	statement.Exec()

	channel := make(chan Visit)

	go saver(db, channel)

	http.HandleFunc("/track", func(w http.ResponseWriter, r *http.Request) {
		visit := make(map[string]string)

		//
		// Input validation
		//
		var user string
		uuid := r.FormValue("id")
		if uuid == "" {
			userId := r.FormValue("user")
			if userId == "" {
				// this has to be supported until the end of time, or
				// alternatively all current users are not using that option.
				userId = r.FormValue("site")
				if userId == "" {
					w.WriteHeader(http.StatusBadRequest)
					w.Write([]byte("missing site param\n"))
					return
				}
			}
			user = userId
		} else {
			user = uuid
		}

		//
		// variables
		//
		now := TimeNow(ParseUTCOffset(r, "utcoffset"))
		userAgent := r.Header.Get("User-Agent")
		ua := uasurfer.Parse(userAgent)
		origin := r.Header.Get("Origin")

		// XXXXXXXXXXXX UNCOMMENT!!!
		// if origin == "" || origin == "null" {
		// 	w.WriteHeader(http.StatusBadRequest)
		// 	w.Write([]byte("Origin header can not be empty, not set or \"null\"\n"))
		// }

		// ignore some origins
		if strings.HasSuffix(origin, ".translate.goog") {
			w.WriteHeader(http.StatusBadRequest)
			w.Write([]byte("Ignoring due origin\n"))
		}

		//
		// set expire
		//
		w.Header().Set("Expires", now.Format("Mon, 2 Jan 2006")+" 23:59:59 GMT")

		//
		// Not strictly necessary but avoids the browser issuing an error.
		//
		w.Header().Set("Access-Control-Allow-Origin", "*")

		//
		// drop if bot or origin is from localhost
		// see issue: https://github.com/avct/uasurfer/issues/65
		//
		if ua.IsBot() || strings.Contains(userAgent, " HeadlessChrome/") || strings.Contains(userAgent, "PetalBot;") || strings.Contains(userAgent, "AdsBot") {
			return
		}
		originUrl, err := url.Parse(origin)
		if err == nil && (originUrl.Hostname() == "localhost" || originUrl.Hostname() == "127.0.0.1") {
			return
		}

		//
		// build visit map
		//

		refParam := r.FormValue("referrer")
		parsedUrl, err := url.Parse(refParam)
		if err == nil && parsedUrl.Host != "" {
			visit["ref"] = parsedUrl.Host
		}

		ref := r.Header.Get("Referer")

		parsedUrl, err = url.Parse(ref)
		if err == nil && parsedUrl.Path != "" {
			visit["loc"] = parsedUrl.Path
		}

		tags, _, err := language.ParseAcceptLanguage(r.Header.Get("Accept-Language"))
		if err == nil && len(tags) > 0 {
			lang := display.English.Languages().Name(tags[0])
			visit["lang"] = lang
		}

		country := r.FormValue("country")
		if country == "" {
			country = r.Header.Get("CF-IPCountry")
		}

		if country != "" && country != "XX" {
			visit["country"] = strings.ToLower(country)
		}

		screenInput := r.FormValue("screen")
		if screenInput != "" {
			_, screenExists := ScreenResolutions[screenInput]
			if screenExists {
				visit["screen"] = screenInput
			} else {
				visit["screen"] = "Other"
			}
		}

		device := ua.DeviceType.StringTrimPrefix()

		visit["date"] = now.Format("2006-01-02")

		visit["weekday"] = fmt.Sprintf("%d", now.Weekday())

		visit["hour"] = fmt.Sprintf("%d", now.Hour())

		visit["browser"] = ua.Browser.Name.StringTrimPrefix()

		visit["device"] = device

		var platform string
		// Show "Android" on android devices instead of "Linux".
		if ua.OS.Name == uasurfer.OSAndroid {
			platform = "Android"
		} else {
			platform = ua.OS.Platform.StringTrimPrefix()

		}
		visit["platform"] = platform

		//
		// save visit map
		//
		// logLine := fmt.Sprintf("[%s] %s %s %s %s", now.Format("2006-01-02 15:04:05"), country, refParam, device, platform)

		domain := Origin2SiteId(origin)

		channel <- Visit{user, domain, now.Format("2006-01-02"), visit}

		w.Header().Set("Content-Type", "text/plain")
		w.Header().Set("Cache-Control", "public, immutable")
		w.WriteHeader(http.StatusNoContent)
		w.Write([]byte(""))

	})

	fmt.Println("Serving...")
	err = http.ListenAndServe(":3333", nil)
	if err != nil {
		panic(fmt.Sprintf("ListenAndServe: %s", err))
	}
}
