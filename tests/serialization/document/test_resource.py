from __future__ import unicode_literals

from collections import OrderedDict

import pytest

from flask_jsonapi.serialization import document


@pytest.fixture
def book(db, models, fantasy_database):
    return db.session.query(models.Book).filter_by(id=11).one()


@pytest.fixture
def series(db, models, fantasy_database):
    return db.session.query(models.Series).filter_by(id=1).one()


def test_single_resource(jsonapi, resource_registry, book, db):
    data = document.resource.dump(
        resource=resource_registry.by_type['books'],
        model=book
    )
    assert data == {
        "data": {
            "type": "books",
            "id": "11",
            "links": {
                "self": "http://example.com/books/11"
            },
            "attributes": {
                "title": "The Hobbit",
                "date_published": "1937-09-21"
            },
            "relationships": {
                "author": {
                    "links": {
                        "self":
                            "http://example.com/books/11/relationships/author",
                        "related": "http://example.com/books/11/author"
                    },
                    "data": {
                        "type": "authors",
                        "id": "1"
                    }
                },
                "chapters": {
                    "links": {
                        "self":
                            "http://example.com/books/11/relationships"
                            "/chapters",
                        "related": "http://example.com/books/11/chapters"
                    },
                    "data": [
                        {"id": "271", "type": "chapters"},
                        {"id": "272", "type": "chapters"},
                        {"id": "273", "type": "chapters"},
                        {"id": "274", "type": "chapters"},
                        {"id": "275", "type": "chapters"},
                        {"id": "276", "type": "chapters"},
                        {"id": "277", "type": "chapters"},
                        {"id": "278", "type": "chapters"},
                        {"id": "279", "type": "chapters"},
                        {"id": "280", "type": "chapters"},
                        {"id": "281", "type": "chapters"},
                        {"id": "282", "type": "chapters"},
                        {"id": "283", "type": "chapters"},
                        {"id": "284", "type": "chapters"},
                        {"id": "285", "type": "chapters"},
                        {"id": "286", "type": "chapters"},
                        {"id": "287", "type": "chapters"},
                        {"id": "288", "type": "chapters"},
                        {"id": "289", "type": "chapters"},
                    ]
                },
                "series": {
                    "links": {
                        "self":
                            "http://example.com/books/11/relationships/series",
                        "related": "http://example.com/books/11/series"
                    },
                    "data": None
                },
                "stores": {
                    "links": {
                        "self":
                            "http://example.com/books/11/relationships/stores",
                        "related": "http://example.com/books/11/stores"
                    },
                }
            }
        }
    }


def test_null_resource(jsonapi, resource_registry, db):
    data = document.resource.dump(
        resource=resource_registry.by_type['books'],
        model=None
    )
    assert data == {
        "data": None
    }


def test_sparse_fieldsets(jsonapi, resource_registry, book, db):
    data = document.resource.dump(
        resource=resource_registry.by_type['books'],
        model=book,
        fields={'books': {'title', 'author'}}
    )
    assert data == {
        "data": {
            "type": "books",
            "id": "11",
            "links": {
                "self": "http://example.com/books/11"
            },
            "attributes": {
                "title": "The Hobbit",
            },
            "relationships": {
                "author": {
                    "links": {
                        "self":
                            "http://example.com/books/11/relationships/author",
                        "related": "http://example.com/books/11/author"
                    },
                    "data": {
                        "type": "authors",
                        "id": "1"
                    }
                },
            }
        }
    }


def test_inclusion_of_related_resources(
    jsonapi, resource_registry, series, db
):
    data = document.resource.dump(
        resource=resource_registry.by_type['series'],
        model=series,
        fields={
            'authors': {'name'},
            'books': {'title', 'author', 'chapters'},
            'chapters': {'title'},
            'series': {'title', 'books'},
        },
        include=OrderedDict([
            ('books', OrderedDict([
                ('author', OrderedDict()),
                ('chapters', OrderedDict()),
            ]))
        ])
    )
    assert len(data['included']) == 66
    assert data == {
        "data": {
            "type": "series",
            "id": "1",
            "attributes": {
                "title": "The Lord of the Rings"
            },
            "relationships": {
                "books": {
                    "data": [
                        {"type": "books", "id": "1"},
                        {"type": "books", "id": "2"},
                        {"type": "books", "id": "3"}
                    ],
                    "links": {
                        "related": "http://example.com/series/1/books",
                        "self": (
                            "http://example.com/series/1/relationships/books"
                        )
                    }
                }
            },
            "links": {
                "self": "http://example.com/series/1"
            }
        },
        "included": [
            {
                "type": "books",
                "id": "1",
                "attributes": {
                    "title": "The Fellowship of the Ring"
                },
                "relationships": {
                    "author": {
                        "data": {"type": "authors", "id": "1"},
                        "links": {
                            "related": "http://example.com/books/1/author",
                            "self": (
                                "http://example.com/books/1/relationships"
                                "/author"
                            )
                        }
                    },
                    "chapters": {
                        "data": [
                            {"type": "chapters", "id": "1"},
                            {"type": "chapters", "id": "2"},
                            {"type": "chapters", "id": "3"},
                            {"type": "chapters", "id": "4"},
                            {"type": "chapters", "id": "5"},
                            {"type": "chapters", "id": "6"},
                            {"type": "chapters", "id": "7"},
                            {"type": "chapters", "id": "8"},
                            {"type": "chapters", "id": "9"},
                            {"type": "chapters", "id": "10"},
                            {"type": "chapters", "id": "11"},
                            {"type": "chapters", "id": "12"},
                            {"type": "chapters", "id": "13"},
                            {"type": "chapters", "id": "14"},
                            {"type": "chapters", "id": "15"},
                            {"type": "chapters", "id": "16"},
                            {"type": "chapters", "id": "17"},
                            {"type": "chapters", "id": "18"},
                            {"type": "chapters", "id": "19"},
                            {"type": "chapters", "id": "20"},
                            {"type": "chapters", "id": "21"},
                            {"type": "chapters", "id": "22"}
                        ],
                        "links": {
                            "related": "http://example.com/books/1/chapters",
                            "self": (
                                "http://example.com/books/1/relationships"
                                "/chapters"
                            )
                        }
                    }
                },
                "links": {
                    "self": "http://example.com/books/1"
                }
            },
            {
                "type": "authors",
                "id": "1",
                "attributes": {
                    "name": "J. R. R. Tolkien"
                },
                "links": {
                    "self": "http://example.com/authors/1"
                }
            },
            {
                "type": "chapters",
                "id": "1",
                "attributes": {
                    "title": "A Long-expected Party"
                },
                "links": {
                    "self": "http://example.com/chapters/1"
                }
            },
            {
                "type": "chapters",
                "id": "2",
                "attributes": {
                    "title": "The Shadow of the Past"
                },
                "links": {
                    "self": "http://example.com/chapters/2"
                }
            },
            {
                "type": "chapters",
                "id": "3",
                "attributes": {
                    "title": "Three is Company"
                },
                "links": {
                    "self": "http://example.com/chapters/3"
                }
            },
            {
                "type": "chapters",
                "id": "4",
                "attributes": {
                    "title": "A Short Cut to Mushrooms"
                },
                "links": {
                    "self": "http://example.com/chapters/4"
                }
            },
            {
                "type": "chapters",
                "id": "5",
                "attributes": {
                    "title": "A Conspiracy Unmasked"
                },
                "links": {
                    "self": "http://example.com/chapters/5"
                }
            },
            {
                "type": "chapters",
                "id": "6",
                "attributes": {
                    "title": "The Old Forest"
                },
                "links": {
                    "self": "http://example.com/chapters/6"
                }
            },
            {
                "type": "chapters",
                "id": "7",
                "attributes": {
                    "title": "In the House of Tom Bombadil"
                },
                "links": {
                    "self": "http://example.com/chapters/7"
                }
            },
            {
                "type": "chapters",
                "id": "8",
                "attributes": {
                    "title": "Fog on the Barrow-downs"
                },
                "links": {
                    "self": "http://example.com/chapters/8"
                }
            },
            {
                "type": "chapters",
                "id": "9",
                "attributes": {
                    "title": "At the Sign of the Prancing Pony"
                },
                "links": {
                    "self": "http://example.com/chapters/9"
                }
            },
            {
                "type": "chapters",
                "id": "10",
                "attributes": {
                    "title": "Strider"
                },
                "links": {
                    "self": "http://example.com/chapters/10"
                }
            },
            {
                "type": "chapters",
                "id": "11",
                "attributes": {
                    "title": "A Knife in the Dark"
                },
                "links": {
                    "self": "http://example.com/chapters/11"
                }
            },
            {
                "type": "chapters",
                "id": "12",
                "attributes": {
                    "title": "Flight to the Ford"
                },
                "links": {
                    "self": "http://example.com/chapters/12"
                }
            },
            {
                "type": "chapters",
                "id": "13",
                "attributes": {
                    "title": "Many Meetings"
                },
                "links": {
                    "self": "http://example.com/chapters/13"
                }
            },
            {
                "type": "chapters",
                "id": "14",
                "attributes": {
                    "title": "The Council of Elrond"
                },
                "links": {
                    "self": "http://example.com/chapters/14"
                }
            },
            {
                "type": "chapters",
                "id": "15",
                "attributes": {
                    "title": "The Ring goes South"
                },
                "links": {
                    "self": "http://example.com/chapters/15"
                }
            },
            {
                "type": "chapters",
                "id": "16",
                "attributes": {
                    "title": "A Journey in the Dark"
                },
                "links": {
                    "self": "http://example.com/chapters/16"
                }
            },
            {
                "type": "chapters",
                "id": "17",
                "attributes": {
                    "title": "The Bridge of Khazad-d\xfbm"
                },
                "links": {
                    "self": "http://example.com/chapters/17"
                }
            },
            {
                "type": "chapters",
                "id": "18",
                "attributes": {
                    "title": "Lothl\xf3rien"
                },
                "links": {
                    "self": "http://example.com/chapters/18"
                }
            },
            {
                "type": "chapters",
                "id": "19",
                "attributes": {
                    "title": "The Mirror of Galadriel"
                },
                "links": {
                    "self": "http://example.com/chapters/19"
                }
            },
            {
                "type": "chapters",
                "id": "20",
                "attributes": {
                    "title": "Farewell to L\xf3rien"
                },
                "links": {
                    "self": "http://example.com/chapters/20"
                }
            },
            {
                "type": "chapters",
                "id": "21",
                "attributes": {
                    "title": "The Great River"
                },
                "links": {
                    "self": "http://example.com/chapters/21"
                }
            },
            {
                "type": "chapters",
                "id": "22",
                "attributes": {
                    "title": "The Breaking of the Fellowship"
                },
                "links": {
                    "self": "http://example.com/chapters/22"
                }
            },
            {
                "id": "2",
                "attributes": {
                    "title": "The Two Towers"
                },
                "links": {
                    "self": "http://example.com/books/2"
                },
                "relationships": {
                    "author": {
                        "data": {"type": "authors", "id": "1"},
                        "links": {
                            "related": "http://example.com/books/2/author",
                            "self": (
                                "http://example.com/books/2/relationships"
                                "/author"
                            )
                        }
                    },
                    "chapters": {
                        "data": [
                            {"type": "chapters", "id": "23"},
                            {"type": "chapters", "id": "24"},
                            {"type": "chapters", "id": "25"},
                            {"type": "chapters", "id": "26"},
                            {"type": "chapters", "id": "27"},
                            {"type": "chapters", "id": "28"},
                            {"type": "chapters", "id": "29"},
                            {"type": "chapters", "id": "30"},
                            {"type": "chapters", "id": "31"},
                            {"type": "chapters", "id": "32"},
                            {"type": "chapters", "id": "33"},
                            {"type": "chapters", "id": "34"},
                            {"type": "chapters", "id": "35"},
                            {"type": "chapters", "id": "36"},
                            {"type": "chapters", "id": "37"},
                            {"type": "chapters", "id": "38"},
                            {"type": "chapters", "id": "39"},
                            {"type": "chapters", "id": "40"},
                            {"type": "chapters", "id": "41"},
                            {"type": "chapters", "id": "42"},
                            {"type": "chapters", "id": "43"}
                        ],
                        "links": {
                            "related": "http://example.com/books/2/chapters",
                            "self": (
                                "http://example.com/books/2/relationships"
                                "/chapters"
                            )
                        }
                    }
                },
                "type": "books"
            },
            {
                "type": "chapters",
                "id": "23",
                "attributes": {
                    "title": "The Departure of Boromir"
                },
                "links": {
                    "self": "http://example.com/chapters/23"
                }
            },
            {
                "type": "chapters",
                "id": "24",
                "attributes": {
                    "title": "The Riders of Rohan"
                },
                "links": {
                    "self": "http://example.com/chapters/24"
                }
            },
            {
                "type": "chapters",
                "id": "25",
                "attributes": {
                    "title": "The Uruk-hai"
                },
                "links": {
                    "self": "http://example.com/chapters/25"
                }
            },
            {
                "type": "chapters",
                "id": "26",
                "attributes": {
                    "title": "Treebeard"
                },
                "links": {
                    "self": "http://example.com/chapters/26"
                }
            },
            {
                "type": "chapters",
                "id": "27",
                "attributes": {
                    "title": "The White Rider"
                },
                "links": {
                    "self": "http://example.com/chapters/27"
                }
            },
            {
                "type": "chapters",
                "id": "28",
                "attributes": {
                    "title": "The King of the Golden Hall"
                },
                "links": {
                    "self": "http://example.com/chapters/28"
                }
            },
            {
                "type": "chapters",
                "id": "29",
                "attributes": {
                    "title": "Helm's Deep"
                },
                "links": {
                    "self": "http://example.com/chapters/29"
                }
            },
            {
                "type": "chapters",
                "id": "30",
                "attributes": {
                    "title": "The Road to Isengard"
                },
                "links": {
                    "self": "http://example.com/chapters/30"
                }
            },
            {
                "type": "chapters",
                "id": "31",
                "attributes": {
                    "title": "Flotsam and Jetsam"
                },
                "links": {
                    "self": "http://example.com/chapters/31"
                }
            },
            {
                "type": "chapters",
                "id": "32",
                "attributes": {
                    "title": "The Voice of Saruman"
                },
                "links": {
                    "self": "http://example.com/chapters/32"
                }
            },
            {
                "type": "chapters",
                "id": "33",
                "attributes": {
                    "title": "The Palant\xedr"
                },
                "links": {
                    "self": "http://example.com/chapters/33"
                }
            },
            {
                "type": "chapters",
                "id": "34",
                "attributes": {
                    "title": "The Taming of Smeagol"
                },
                "links": {
                    "self": "http://example.com/chapters/34"
                }
            },
            {
                "type": "chapters",
                "id": "35",
                "attributes": {
                    "title": "The Passage of the Marshes"
                },
                "links": {
                    "self": "http://example.com/chapters/35"
                }
            },
            {
                "type": "chapters",
                "id": "36",
                "attributes": {
                    "title": "The Black Gate is Closed"
                },
                "links": {
                    "self": "http://example.com/chapters/36"
                }
            },
            {
                "type": "chapters",
                "id": "37",
                "attributes": {
                    "title": "Of Herbs and Stewed Rabbit"
                },
                "links": {
                    "self": "http://example.com/chapters/37"
                }
            },
            {
                "type": "chapters",
                "id": "38",
                "attributes": {
                    "title": "The Window on the West"
                },
                "links": {
                    "self": "http://example.com/chapters/38"
                }
            },
            {
                "type": "chapters",
                "id": "39",
                "attributes": {
                    "title": "The Forbidden Pool"
                },
                "links": {
                    "self": "http://example.com/chapters/39"
                }
            },
            {
                "type": "chapters",
                "id": "40",
                "attributes": {
                    "title": "Journey to the Cross-roads"
                },
                "links": {
                    "self": "http://example.com/chapters/40"
                }
            },
            {
                "type": "chapters",
                "id": "41",
                "attributes": {
                    "title": "The Stairs of Cirith Ungol"
                },
                "links": {
                    "self": "http://example.com/chapters/41"
                }
            },
            {
                "type": "chapters",
                "id": "42",
                "attributes": {
                    "title": "Shelob's Lair"
                },
                "links": {
                    "self": "http://example.com/chapters/42"
                }
            },
            {
                "type": "chapters",
                "id": "43",
                "attributes": {
                    "title": "The Choices of Master Samwise"
                },
                "links": {
                    "self": "http://example.com/chapters/43"
                }
            },
            {
                "type": "books",
                "id": "3",
                "attributes": {
                    "title": "Return of the King"
                },
                "relationships": {
                    "author": {
                        "data": {"type": "authors", "id": "1"},
                        "links": {
                            "related": "http://example.com/books/3/author",
                            "self": (
                                "http://example.com/books/3/relationships"
                                "/author"
                            )
                        }
                    },
                    "chapters": {
                        "data": [
                            {"type": "chapters", "id": "44"},
                            {"type": "chapters", "id": "45"},
                            {"type": "chapters", "id": "46"},
                            {"type": "chapters", "id": "47"},
                            {"type": "chapters", "id": "48"},
                            {"type": "chapters", "id": "49"},
                            {"type": "chapters", "id": "50"},
                            {"type": "chapters", "id": "51"},
                            {"type": "chapters", "id": "52"},
                            {"type": "chapters", "id": "53"},
                            {"type": "chapters", "id": "54"},
                            {"type": "chapters", "id": "55"},
                            {"type": "chapters", "id": "56"},
                            {"type": "chapters", "id": "57"},
                            {"type": "chapters", "id": "58"},
                            {"type": "chapters", "id": "59"},
                            {"type": "chapters", "id": "60"},
                            {"type": "chapters", "id": "61"},
                            {"type": "chapters", "id": "62"}
                        ],
                        "links": {
                            "related": "http://example.com/books/3/chapters",
                            "self": (
                                "http://example.com/books/3/relationships"
                                "/chapters"
                            )
                        }
                    }
                },
                "links": {
                    "self": "http://example.com/books/3"
                }
            },
            {
                "type": "chapters",
                "id": "44",
                "attributes": {
                    "title": "Minas Tirith"
                },
                "links": {
                    "self": "http://example.com/chapters/44"
                }
            },
            {
                "type": "chapters",
                "id": "45",
                "attributes": {
                    "title": "The Passing of the Grey Company"
                },
                "links": {
                    "self": "http://example.com/chapters/45"
                }
            },
            {
                "type": "chapters",
                "id": "46",
                "attributes": {
                    "title": "The Muster of Rohan"
                },
                "links": {
                    "self": "http://example.com/chapters/46"
                }
            },
            {
                "type": "chapters",
                "id": "47",
                "attributes": {
                    "title": "The Siege of Gondor"
                },
                "links": {
                    "self": "http://example.com/chapters/47"
                }
            },
            {
                "type": "chapters",
                "id": "48",
                "attributes": {
                    "title": "The Ride of the Rohirrim"
                },
                "links": {
                    "self": "http://example.com/chapters/48"
                }
            },
            {
                "type": "chapters",
                "id": "49",
                "attributes": {
                    "title": "The Battle of the Pelennor Fields"
                },
                "links": {
                    "self": "http://example.com/chapters/49"
                }
            },
            {
                "type": "chapters",
                "id": "50",
                "attributes": {
                    "title": "The Pyre of Denethor"
                },
                "links": {
                    "self": "http://example.com/chapters/50"
                }
            },
            {
                "type": "chapters",
                "id": "51",
                "attributes": {
                    "title": "The Houses of Healing"
                },
                "links": {
                    "self": "http://example.com/chapters/51"
                }
            },
            {
                "type": "chapters",
                "id": "52",
                "attributes": {
                    "title": "The Last Debate"
                },
                "links": {
                    "self": "http://example.com/chapters/52"
                }
            },
            {
                "type": "chapters",
                "id": "53",
                "attributes": {
                    "title": "The Black Gate Opens"
                },
                "links": {
                    "self": "http://example.com/chapters/53"
                }
            },
            {
                "type": "chapters",
                "id": "54",
                "attributes": {
                    "title": "The Tower of Cirith Ungol"
                },
                "links": {
                    "self": "http://example.com/chapters/54"
                }
            },
            {
                "type": "chapters",
                "id": "55",
                "attributes": {
                    "title": "The Land of Shadow"
                },
                "links": {
                    "self": "http://example.com/chapters/55"
                }
            },
            {
                "type": "chapters",
                "id": "56",
                "attributes": {
                    "title": "Mount Doom"
                },
                "links": {
                    "self": "http://example.com/chapters/56"
                }
            },
            {
                "type": "chapters",
                "id": "57",
                "attributes": {
                    "title": "The Field of Cormallen"
                },
                "links": {
                    "self": "http://example.com/chapters/57"
                }
            },
            {
                "type": "chapters",
                "id": "58",
                "attributes": {
                    "title": "The Steward and the King"
                },
                "links": {
                    "self": "http://example.com/chapters/58"
                }
            },
            {
                "type": "chapters",
                "id": "59",
                "attributes": {
                    "title": "Many Partings"
                },
                "links": {
                    "self": "http://example.com/chapters/59"
                }
            },
            {
                "type": "chapters",
                "id": "60",
                "attributes": {
                    "title": "Homeward Bound"
                },
                "links": {
                    "self": "http://example.com/chapters/60"
                }
            },
            {
                "type": "chapters",
                "id": "61",
                "attributes": {
                    "title": "The Scouring of the Shire"
                },
                "links": {
                    "self": "http://example.com/chapters/61"
                }
            },
            {
                "type": "chapters",
                "id": "62",
                "attributes": {
                    "title": "The Grey Havens"
                },
                "links": {
                    "self": "http://example.com/chapters/62"
                }
            }
        ]
    }
