/**
 * Railroad Drawer v1.0.0
 * Governed view port into server execution
 * 
 * Philosophy:
 * - Client declares intent
 * - Server owns execution
 * - Drawer is just a viewport
 * 
 * Part of the Railroad ecosystem.
 */

(function(window) {
  'use strict';

  const RailroadDrawer = {
    // Configuration
    config: {
      endpoint: '/drawer/',
      position: 'right',
      size: 'medium',
      backdrop: true,
      keyboard: true
    },

    // State
    currentDrawer: null,
    isOpen: false,

    /**
     * Initialize drawer system
     */
    init: function(config = {}) {
      Object.assign(this.config, config);
      this._createDrawerElements();
      this._attachEventListeners();
      console.log('[Railroad Drawer] Initialized');
    },

    /**
     * Open drawer with governed server execution
     * @param {string} view - Server-registered view name
     * @param {object} args - Allowed parameters for that view
     * @param {object} options - drawer options (position, size, etc.)
     */
    open: function(view, args = {}, options = {}) {
      const position = options.position || this.config.position;
      const size = options.size || this.config.size;

      // Show loader if available
      if (window.RailroadLoader) {
        window.RailroadLoader.show([`Loading ${view}...`]);
      }

      // Prepare request - client only sends intent + params
      const payload = {
        view: view,
        args: args
      };

      // Request governed server execution
      fetch(this.config.endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify(payload)
      })
      .then(response => {
        if (!response.ok) {
          throw new Error(`Drawer error: ${response.status}`);
        }
        return response.text();
      })
      .then(html => {
        this._renderDrawer(html, position, size);
        
        // Rebind if Railroad Runtime present
        if (window.RAILROAD) {
          const content = document.querySelector('.railroad-drawer-content');
          window.RAILROAD.rebind(content, `drawer-${view}`);
        }

        // Hide loader
        if (window.RailroadLoader) {
          window.RailroadLoader.hide();
        }
      })
      .catch(err => {
        console.error('[Railroad Drawer] Error:', err);
        
        // Hide loader
        if (window.RailroadLoader) {
          window.RailroadLoader.hide();
        }

        // Show error toast if available
        if (window.toast) {
          window.toast(`Failed to load ${view}`, 'error');
        }
      });
    },

    /**
     * Close drawer
     */
    close: function() {
      const drawer = document.querySelector('.railroad-drawer');
      const backdrop = document.querySelector('.railroad-drawer-backdrop');
      
      if (drawer) {
        drawer.classList.remove('open');
      }
      
      if (backdrop) {
        backdrop.classList.remove('visible');
      }

      this.isOpen = false;
      this.currentDrawer = null;

      // Clean up content after animation
      setTimeout(() => {
        const content = document.querySelector('.railroad-drawer-content');
        if (content) {
          content.innerHTML = '';
        }
      }, 300);
    },

    /**
     * Create drawer DOM elements
     */
    _createDrawerElements: function() {
      // Create backdrop
      const backdrop = document.createElement('div');
      backdrop.className = 'railroad-drawer-backdrop';
      backdrop.addEventListener('click', () => this.close());
      document.body.appendChild(backdrop);

      // Create drawer container
      const drawer = document.createElement('div');
      drawer.className = 'railroad-drawer';
      drawer.innerHTML = `
        <div class="railroad-drawer-header">
          <button class="railroad-drawer-close" aria-label="Close drawer">×</button>
        </div>
        <div class="railroad-drawer-content"></div>
      `;
      document.body.appendChild(drawer);

      // Inject styles
      this._injectStyles();
    },

    /**
     * Render drawer content
     */
    _renderDrawer: function(html, position, size) {
      const drawer = document.querySelector('.railroad-drawer');
      const backdrop = document.querySelector('.railroad-drawer-backdrop');
      const content = document.querySelector('.railroad-drawer-content');

      // Set position and size
      drawer.className = `railroad-drawer ${position} ${size}`;
      
      // Set content
      content.innerHTML = html;

      // Show drawer
      setTimeout(() => {
        drawer.classList.add('open');
        backdrop.classList.add('visible');
      }, 10);

      this.isOpen = true;
      this.currentDrawer = { position, size };
    },

    /**
     * Attach event listeners
     */
    _attachEventListeners: function() {
      // Close button
      document.addEventListener('click', (e) => {
        if (e.target.classList.contains('railroad-drawer-close')) {
          this.close();
        }
      });

      // Keyboard support (ESC)
      if (this.config.keyboard) {
        document.addEventListener('keydown', (e) => {
          if (e.key === 'Escape' && this.isOpen) {
            this.close();
          }
        });
      }

      // Declarative drawer triggers
      document.addEventListener('click', (e) => {
        const trigger = e.target.closest('[data-drawer-view]');
        if (!trigger) return;

        e.preventDefault();
        
        const view = trigger.dataset.drawerView;
        const args = trigger.dataset.drawerArgs 
          ? JSON.parse(trigger.dataset.drawerArgs)
          : {};
        const position = trigger.dataset.drawerPosition || this.config.position;
        const size = trigger.dataset.drawerSize || this.config.size;

        this.open(view, args, { position, size });
      });

      // Close drawer triggers
      document.addEventListener('click', (e) => {
        if (e.target.closest('[data-drawer-close]')) {
          e.preventDefault();
          this.close();
        }
      });
    },

    /**
     * Inject drawer styles
     */
    _injectStyles: function() {
      if (document.getElementById('railroad-drawer-styles')) return;

      const styles = document.createElement('style');
      styles.id = 'railroad-drawer-styles';
      styles.textContent = `
        .railroad-drawer-backdrop {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.5);
          opacity: 0;
          visibility: hidden;
          transition: opacity 0.3s, visibility 0.3s;
          z-index: 9998;
        }

        .railroad-drawer-backdrop.visible {
          opacity: 1;
          visibility: visible;
        }

        .railroad-drawer {
          position: fixed;
          top: 0;
          bottom: 0;
          background: #ffffff;
          box-shadow: 0 0 20px rgba(0,0,0,0.15);
          z-index: 9999;
          display: flex;
          flex-direction: column;
          transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .railroad-drawer.right {
          right: 0;
          transform: translateX(100%);
        }

        .railroad-drawer.left {
          left: 0;
          transform: translateX(-100%);
        }

        .railroad-drawer.open {
          transform: translateX(0);
        }

        .railroad-drawer.narrow { width: 300px; }
        .railroad-drawer.medium { width: 400px; }
        .railroad-drawer.wide { width: 600px; }
        .railroad-drawer.full { width: 100%; max-width: 800px; }

        @media (max-width: 768px) {
          .railroad-drawer.narrow,
          .railroad-drawer.medium,
          .railroad-drawer.wide {
            width: 85vw;
          }
        }

        .railroad-drawer-header {
          padding: 20px;
          border-bottom: 1px solid #e5e7eb;
          display: flex;
          justify-content: flex-end;
        }

        .railroad-drawer-close {
          background: none;
          border: none;
          font-size: 32px;
          color: #6b7280;
          cursor: pointer;
          width: 40px;
          height: 40px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 4px;
          transition: background 0.2s, color 0.2s;
        }

        .railroad-drawer-close:hover {
          background: #f3f4f6;
          color: #111827;
        }

        .railroad-drawer-content {
          flex: 1;
          overflow-y: auto;
          padding: 20px;
        }

        /* Dark theme support */
        @media (prefers-color-scheme: dark) {
          .railroad-drawer {
            background: #1f2937;
            color: #f9fafb;
          }

          .railroad-drawer-header {
            border-bottom-color: #374151;
          }

          .railroad-drawer-close {
            color: #9ca3af;
          }

          .railroad-drawer-close:hover {
            background: #374151;
            color: #f9fafb;
          }
        }
      `;
      document.head.appendChild(styles);
    }
  };

  // Auto-initialize when DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => RailroadDrawer.init());
  } else {
    RailroadDrawer.init();
  }

  // Export
  window.RailroadDrawer = RailroadDrawer;

  // CommonJS support
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = RailroadDrawer;
  }

})(typeof window !== 'undefined' ? window : this);
