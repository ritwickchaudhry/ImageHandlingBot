 (function() {
     var tabManager = window.tabManager || {};
     var ACTIVE_CLASS = 'is-active';
     var forEach = Function.prototype.call.bind(Array.prototype.forEach);

     tabManager.initTabs = function() {
          var tabs = document.querySelectorAll('.tab-item');
          var contentPanels = document.querySelectorAll('.content-panel');

          function getCurrentTabName() {
              var element = document.querySelector('.tab-item.' + ACTIVE_CLASS);
              return element.getAttribute('data-tab');
          }

          function selectTab(tabName) {
              if (getCurrentTabName() !== tabName) {
                  var currentTab = document.querySelector('.tab-item[data-tab=' + tabName + ']');

                  forEach(tabs, function(tab) { tab.classList.remove(ACTIVE_CLASS); });
                  currentTab.classList.add(ACTIVE_CLASS);

                  forEach(contentPanels, function(panel) { panel.classList.remove(ACTIVE_CLASS); });
                  document.querySelector('.panel--' + tabName).classList.add(ACTIVE_CLASS);
              }
          }

          function validateTabs() {
              //currently the only validation needed is we need to remove the shapes tab when in embroidery
              if (!window.dcl.featureManager.featureEnabled('addShape')) {
                  var shapeTab = document.querySelector('.tab-item[data-tab=shapes]');
                  shapeTab.remove();
              }
              forEach(tabs, function(tab) { tab.classList.add('visible'); });
          }

          forEach(tabs, function(tab) {
              tab.addEventListener('click', function(e) {
                  e.preventDefault();
                  selectTab(this.getAttribute('data-tab'));
              });
          });

          window.dcl.eventBus.on(window.dcl.eventBus.events.uploadStarted, function() {
              selectTab('images');
          });

          window.dcl.eventBus.on(window.dcl.eventBus.events.engineStarted, function() {
              validateTabs();
          });
      };

     window.tabManager = tabManager;
 })();
