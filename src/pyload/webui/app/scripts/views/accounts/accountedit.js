define(['jquery', 'underscore', 'app', 'views/abstract/modalview', 'views/input/inputrenderer', 'hbs!tpl/accounts/editaccount', 'hbs!tpl/settings/configitem'],
  function($, _, App, modalView, renderForm, template, templateItem) {
    'use strict';
    return modalView.extend({

      events: {
        'click .btn-save': 'save',
        'submit form': 'save'
      },

      template: template,

      initialize: function() {
        // Inherit parent events
        this.events = _.extend({}, modalView.prototype.events, this.events);
      },

      onRender: function() {
        renderForm(this.$('.account-config'),
          this.model.get('config'),
          templateItem
        );
      },

      save: function() {
        var password = this.$('#password').val();
        if (password !== '') {
          this.model.setPassword(password);
        }
        this.model.save();
        this.hide();
        return false;
      },

      onShow: function() {
      },

      onHide: function() {
      }
    });
  });
