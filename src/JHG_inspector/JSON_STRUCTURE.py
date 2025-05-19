SIMPLE_JSON_STRUCTURE = {
    # "miscData": {
    #     "status": "scalar",
    #     "creatorId": "scalar",
    # },
    "lobby": {
        "code": "scalar",
        "numPlayers": "scalar",
        "numObservers": "scalar",
        "creatorName": "scalar",
        # "admins": [],
        # "playerNames": [],
        "gameStarted": "scalar"
    },
    "gameParams": {
        "lengthOfRound": "scalar",
        "nameSet": "scalar",
        "chatType": "scalar",
        "messageType": "scalar",

        "gameEndCriteria": {
            "low": "scalar",
            "high": "scalar",
            "runtimeType": "scalar"
        },

        "popularityFunctionParams": {
            "alpha": "scalar",
            "beta": "scalar",
            "cGive": "scalar",
            "cKeep": "scalar",
            "cSteal": "scalar",
            "povertyLine": "scalar",
            "shouldUseNewUpdate": "scalar"
        },

        "governmentParams": {
            "initialPopularity": "scalar",
            "initialPopularityType": "scalar",
            "randomPopularities": "scalar",
            "randomPopHigh": "scalar",
            "randomPopLow": "scalar",
            "playersThatWillBeGovernment": "scalar",
            "sendVotesImmediately": "scalar"
        },

        # "colorGroups": [],
        # "customParams": {},
        "labels": {
            "enabled": "scalar",
            # "labelPools": []
        },

        "show": {
            "roundLength": "scalar",
            "gameLength": "scalar",
            "chatType": "scalar",
            "messageType": "scalar",
            "nameSet": "scalar",
            "initialSetup": "scalar",
            "grouping": "scalar",
            "labels": "scalar",
            "advancedParams": "scalar",
            "government": "scalar",
            "visibilities": "scalar",
            "colorGrouping": "scalar",
            "pregame": "scalar",
            "agents": "scalar"
        },

        "allowEdit": {
            "roundLength": "scalar",
            "gameLength": "scalar",
            "chatType": "scalar",
            "messageType": "scalar",
            "nameSet": "scalar",
            "initialSetup": "scalar",
            "grouping": "scalar",
            "labels": "scalar",
            "advancedParams": "scalar",
            "government": "scalar",
            "visibilities": "scalar",
            "colorGrouping": "scalar",
            "pregame": "scalar",
            "agents": "scalar"
        }
    },
    "endCondition": {
        "duration": "scalar",
        "runtimeType": "scalar"
    }
}