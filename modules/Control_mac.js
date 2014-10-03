module.exports = (function() {
  console.assert(typeof application !== "undefined", 'You must use require(\'Application\') prior to using any GUI components.');
  console.assert(process.bridge.objc, 'Failure to establish objective-c bridge.');
  
  var $ = process.bridge.objc;
  var utilities = require('Utilities');

  function addTrackingArea() {
    var bounds = this.nativeView('bounds');
    var options = $.NSTrackingMouseEnteredAndExited | $.NSTrackingMouseMoved | $.NSTrackingActiveInActiveApp | $.NSTrackingInVisibleRect;
    this.private.trackingArea = $.NSTrackingArea('alloc')('initWithRect', bounds, 'options', options, 'owner', this.nativeView, 'userInfo', null);
    this.nativeView('addTrackingArea',this.private.trackingArea);
  }

  function createLayoutProperty(name, percentName, percentFunc, scalarName, scalarFunc, na) {
    Object.defineProperty(Control.prototype, name, {
      get: function() { return this.private.user[name]; },
      set: function(value) {
        var p = this.private;

        if(na && na[0] && p.user[na[0]] !== null && na[1] && p.user[na[1]] !== null)
          throw new Error('A '+name+' cannot be set when the '+na[0]+' and '+na[1]+' have been set already.');

        p.user[name] = value;

        var attached = function() {
          this.removeEventListener('parent-attached',attached);
          this[name] = p.user[name];
        }.bind(this);

        if(p.constraints[name] !== null && p.constraints[name])
          p.parent.removeLayoutConstraint(p.constraints[name]);

        if(value == null)
          return;

        this.addEventListener('parent-attached', attached);
        if(!p.parent) return;

        this.addEventListener('parent-dettached', function() {
          p.parent.removeLayoutConstraint(p.constraints[name]);
        }.bind(this));

        var layoutObject = {priority:'required', firstItem:this, firstAttribute:name, relationship:'=', secondItem:p.parent};

        if (value instanceof Control) {
          layoutObject.secondItem = value;
          layoutObject.multiplier = 1.0;
          layoutObject.constant = 0.0;
          if((p.parent == value || this == value.private.parent) 
                || name == "middle" || name == "center") 
          {
            layoutObject.firstAttribute = layoutObject.secondAttribute = name;
          }
          else if (name == "left") {
            layoutObject.firstAttribute = "left";
            layoutObject.secondAttribute = "right";
          } else if (name == "right") {
            layoutObject.firstAttribute = "right";
            layoutObject.secondAttribute = "left";
          } else if (name == "top") {
            layoutObject.firstAttribute = "top";
            layoutObject.secondAttribute = "bottom";
          } else if (name == "bottom") {
            layoutObject.firstAttribute = "bottom";
            layoutObject.secondAttribute = "top";
          }
        } else if(value && value.indexOf && value.indexOf('%') > -1) {
          var parsedValue = utilities.parseUnits(value);
          layoutObject.multiplier = percentFunc(parsedValue);
          layoutObject.constant = 0.0;
          layoutObject.secondAttribute = percentName;
        } else {
          var parsedValue = utilities.parseUnits(value);
          layoutObject.multiplier = 1.0;
          layoutObject.constant = scalarFunc(parsedValue);
          layoutObject.secondAttribute = scalarName;
        }

        if(!layoutObject.secondAttribute) layoutObject.secondItem = null;
        p.constraints[name] = p.parent.addLayoutConstraint(layoutObject);
      }
    });
  }

  function identity(v) { return v; }
  function inverse(v) { return (1-v); }
  function negate(v) { return -1*v; }

  /* Control Class */

  function Control(NativeObjectClass, NativeViewClass, options) {
    options = options || {};
    options.delegates = options.delegates || [];
    if(!options.nonStandardEvents) {
      options.delegates = options.delegates.concat([
        ['mouseDown:','v@:@', function(self, cmd, events) {
            this.fireEvent('mousedown');
            self.super('mouseDown',events);
            if(options.mouseDownBlocks) this.fireEvent('mouseup');
        }.bind(this)],
        ['mouseUp:','v@:@', function(self, cmd, events) { this.fireEvent('mouseup'); self.super('mouseUp',events); }.bind(this)],
        ['rightMouseDown:','v@:@', function(self, cmd, events) { this.fireEvent('rightmousedown'); self.super('rightMouseDown',events); }.bind(this)],
        ['rightMouseUp:','v@:@', function(self, cmd, events) { this.fireEvent('rightmouseup'); self.super('rightMouseUp',events); }.bind(this)],
        ['keyDown:','v@:@', function(self, cmd, events) { this.fireEvent('keydown'); self.super('keyDown',events); }.bind(this)],
        ['keyUp:','v@:@', function(self, cmd, events) { this.fireEvent('keyup'); self.super('keyUp',events); }.bind(this)],
        ['mouseEntered:','v@:@', function(self, cmd, events) { this.fireEvent('mouseenter'); self.super('mouseEntered',events); }.bind(this)],
        ['mouseExited:','v@:@', function(self, cmd, events) { this.fireEvent('mouseexit'); self.super('mouseExited',events); }.bind(this)],
        ['mouseMoved:','v@:@', function(self, cmd, events) { this.fireEvent('mousemove'); self.super('mouseMoved',events); }.bind(this)]
      ]);
    }

    this.private = {
      events:{}, layoutConstraints:[], parent:null, trackingArea:null, needsMouseTracking:0,
      user:{ width:null, height:null, left:null, right:null, top:null, bottom:null, center:null, middle:null },
      constraints:{ width:null, height:null, left:null, right:null, top:null, bottom:null, center:null, middle:null }
    };

    this.nativeClass = NativeObjectClass;
    this.native = this.nativeView = null;

    this.addEventListener('parent-attached', function(p) { this.private.parent = p; }.bind(this));
    this.addEventListener('parent-dettached', function(p) { this.private.parent = null; }.bind(this));

    var nativeViewExtended = NativeViewClass.extend(NativeViewClass.getName()+Math.round(Math.random()*1000000));
    options.delegates.forEach(function(item) {
      nativeViewExtended.addMethod(item[0],item[1],item[2]);
    });
    nativeViewExtended.register();
    this.nativeViewClass = nativeViewExtended;
  }

  Object.defineProperty(Control.prototype, 'alpha', {
    configurable:true,
    get:function() { return this.nativeView('alphaValue'); },
    set:function(e) { return this.nativeView('setAlphaValue', e); }
  });

  Object.defineProperty(Control.prototype, 'visible', {
    configurable:true,
    get:function() { return !this.nativeView('isHidden'); },
    set:function(e) { return this.nativeView('setHidden', !e); }
  });

  // Helper function to convert OSX coordinate spaces to 
  // top-left.
  function convY(frame, parentFrame) {
    frame.origin.y = parentFrame.size.height - frame.origin.y - frame.size.height;
    return frame;
  }

  Object.defineProperty(Control.prototype,'boundsOnScreen', {
    get:function() {
      if(!this.nativeView('superview')) return null;
      var bnds = this.boundsOnWindow;
      var wframe = this.nativeView('window')('frame');
      var wbnds = convY(wframe, $.NSScreen('mainScreen')('frame'));
      return {
        x:Math.round(bnds.x + wbnds.origin.x), 
        y:Math.round(bnds.y + wbnds.origin.y), 
        width:Math.round(bnds.width), 
        height:Math.round(bnds.height)
      };
    }
  });

  Object.defineProperty(Control.prototype,'boundsOnWindow', {
    get:function() {
      if(!this.nativeView('superview')) return null;
      var bnds = convY(this.nativeView('frame'), this.nativeView('window')('frame'));
      return {
        x:Math.round(bnds.origin.x), 
        y:Math.round(bnds.origin.y + (this.private.type != 'Window' ? 1 : 0)), 
        width:Math.round(bnds.size.width), 
        height:Math.round(bnds.size.height)
      };
    }
  });

  Object.defineProperty(Control.prototype,'bounds',{
    get:function() {
      if(!this.nativeView('superview')) return null;
      var bnds = convY(this.nativeView('frame'), this.nativeView('superview')('frame'));
      return {
        x:Math.round(bnds.origin.x), 
        y:Math.round(bnds.origin.y + (this.private.type != 'Window' ? 1 : 0)), 
        width:Math.round(bnds.size.width), 
        height:Math.round(bnds.size.height)
      };
    }
  });

  Control.prototype.fireEvent = function(event, args) {
    try {
      event = event.toLowerCase();
      var returnvalue = undefined;
      if(!this.private.events[event]) this.private.events[event] = [];
      (this.private.events[event]).forEach(function(item,index,arr) { returnvalue = item.apply(null, args) || returnvalue; });
      return returnvalue;
    } catch(e) {
      console.error(e.message);
      console.error(e.stack);
      process.exit(1);
    }
  }

  Control.prototype.addEventListener = function(event, func) {
    event = event.toLowerCase();
    if(event == "mouseenter" || event == "mouseexit" || event == "mousemove") {
      this.private.needsMouseTracking++;
      if(this.private.needsMouseTracking == 1 && this.nativeView('window')) 
        addTrackingArea.apply(this,null);
      else if (this.private.needsMouseTracking == 1)
        this.addEventListener('parent-attached', addTrackingArea.bind(this));
    }
    if(!this.private.events[event]) this.private.events[event] = []; 
    this.private.events[event].push(func);
  }

  Control.prototype.removeEventListener = function(event, func) {
    event = event.toLowerCase();
    if(event == "mouseenter" ||   event == "mouseexit" || event == "mousemove") {
      this.private.needsMouseTracking--;
      if(this.private.needsMouseTracking == 0) {
        this.nativeView('removeTrackingArea',this.private.trackingArea);
        this.private.trackingArea('release');
        this.private.trackingArea = null;
      }
    }
    if(this.private.events[event] && this.private.events[event].indexOf(func) != -1) 
      this.private.events[event].splice(this.private.events[event].indexOf(func), 1);
  }

  var attributeMap = { 'left':$.NSLayoutAttributeLeft, 'right':$.NSLayoutAttributeRight, 'top':$.NSLayoutAttributeTop,
                       'bottom':$.NSLayoutAttributeBottom, 'leading':$.NSLayoutAttributeLeading, 'trailing':$.NSLayoutAttributeTrailing,
                       'width':$.NSLayoutAttributeWidth, 'height':$.NSLayoutAttributeHeight, 'center':$.NSLayoutAttributeCenterX,
                       'middle':$.NSLayoutAttributeCenterY, 'baseline':$.NSLayoutAttributeBaseline, '<':$.NSLayoutRelationLessThanOrEqual,
                       '<=':$.NSLayoutRelationLessThanOrEqual, '>':$.NSLayoutRelationGreaterThanOrEqual, 
                       '>=':$.NSLayoutRelationGreaterThanOrEqual, '=':$.NSLayoutRelationEqual, '==':$.NSLayoutRelationEqual };


  Control.prototype.addLayoutConstraint = function(layoutObject) {
    var constraint = $.NSLayoutConstraint('constraintWithItem',(layoutObject.firstItem ? layoutObject.firstItem.nativeView : layoutObject.item.nativeView),
                        'attribute',(attributeMap[layoutObject.firstAttribute] || $.NSLayoutAttributeNotAnAttribute),
                        'relatedBy',(attributeMap[layoutObject.relationship] || $.NSLayoutRelationEqual),
                        'toItem',(layoutObject.secondItem ? layoutObject.secondItem.nativeView : null),
                        'attribute',(attributeMap[layoutObject.secondAttribute] || $.NSLayoutAttributeNotAnAttribute),
                        'multiplier', (layoutObject.multiplier ? layoutObject.multiplier : 0), 
                        'constant', (layoutObject.constant ? layoutObject.constant : 0));
    this.nativeView('addConstraint',constraint);
    return this.private.layoutConstraints.push({js:layoutObject, native:constraint}) - 1;
  }

  Control.prototype.removeLayoutConstraint = function(index) {
    if(typeof(index) == 'undefined' || index == null || !this.private.layoutConstraints[index]) return;
    var objcNative = this.private.layoutConstraints[index].native;
    this.private.layoutConstraints.splice(index, 1);
    this.nativeView('removeConstraint',objcNative);
    this.nativeView('updateConstraintsForSubtreeIfNeeded');
    this.nativeView('layoutSubtreeIfNeeded');
  }

  createLayoutProperty('top', 'bottom', identity, 'top', identity, ['bottom','height']);
  createLayoutProperty('bottom', 'bottom', inverse, 'bottom', negate, ['top','height']);
  createLayoutProperty('left', 'right', identity, 'left', identity, ['right','width']);
  createLayoutProperty('right', 'right', inverse, 'right', negate, ['left','width']);
  createLayoutProperty('height', 'height', identity, null, identity, ['top','bottom']);
  createLayoutProperty('width', 'width', identity, null, identity, ['left','right']);
  createLayoutProperty('middle', 'middle', identity, 'middle', identity, null);
  createLayoutProperty('center', 'center', identity, 'center', identity, null);

  return Control;
})();