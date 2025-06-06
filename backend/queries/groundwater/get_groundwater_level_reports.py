get_groundwater_level_reports_query = {
    "type": "object",
    "properties": {
        "type": {
            "type": "string"
        },
        "features": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "properties": {
                        "type": "object",
                        "properties": {
                            "id": {
                                "type": "number"
                            },
                            "nid": {
                                "type": "string"
                            },
                            "name": {
                                "type": "string"
                            },
                            "area": {},
                            "net": {
                                "type": "number"
                            },
                            "ty": {
                                "type": "number"
                            },
                            "yr": {
                                "type": "array",
                                "items": {
                                "type": "number"
                                }
                            },
                            "analysesObj": {
                                "type": "object",
                                "properties": {
                                    "1": {
                                        "type": "number"
                                    },
                                    "5": {
                                        "type": "number"
                                    },
                                    "6": {
                                        "type": "number"
                                    },
                                    "7": {
                                        "type": "number"
                                    },
                                    "8": {
                                        "type": "number"
                                    },
                                    "16": {
                                        "type": "number"
                                    },
                                    "19": {
                                        "type": "number"
                                    }
                                }
                            }
                        }
                    },
                    "geometry": {
                        "type": "object",
                        "properties": {
                        "coordinates": {
                            "type": "array",
                            "items": {
                            "type": "number"
                            }
                        },
                        "type": {
                            "type": "string"
                        }
                        }
                    },
                    "type": {
                        "type": "string"
                    }
                }
            }
        }
    }
}
