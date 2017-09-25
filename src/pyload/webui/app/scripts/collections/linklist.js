define(['jquery', 'backbone', 'underscore', 'models/linkstatus'], function($, Backbone, _, LinkStatus) {
  'use strict';

  return Backbone.Collection.extend({

    model: LinkStatus,

    comparator: function(link) {
      return link.get('name');
    }

  });

});
