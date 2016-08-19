 db.getCollection('corp').aggregate([
    {
        $group: {
            _id: "$province",
            total:{$sum:1}
        }
    },
    {
        $sort:{total: -1}
    }
 ])